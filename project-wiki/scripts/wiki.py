#!/usr/bin/env python3
"""Dependency-free project Wiki mechanics. Prose is authored by the Agent."""
import argparse
import fnmatch
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile
from datetime import datetime, timezone
from urllib.parse import unquote

TEMPLATES = Path(__file__).resolve().parents[1] / 'assets' / 'templates'
STATUSES = {'proposed', 'accepted', 'implemented', 'released', 'superseded', 'unknown'}
FRESHNESS = {'fresh', 'stale', 'unknown'}
RELATIONS = {'related', 'describes', 'depends_on', 'implements', 'verified_by', 'supersedes'}
SKIP_DIRS = {'node_modules', 'vendor', 'dist', 'build', '__pycache__'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def safe(base, name):
    """Containment and symlink check, including missing write targets."""
    if not isinstance(name, str) or not name or '\\' in name:
        raise ValueError(f'invalid relative path: {name!r}')
    rel = PurePosixPath(name)
    if rel.is_absolute() or '..' in rel.parts:
        raise ValueError(f'path escapes root: {name}')
    result = base
    for part in rel.parts:
        result = result / part
        if result.is_symlink():
            raise ValueError(f'symbolic link is not allowed: {name}')
    if not result.resolve().is_relative_to(base.resolve()):
        raise ValueError(f'path escapes root: {name}')
    return result


def check_config(config, root):
    if not isinstance(config, dict) or config.get('version') != 1:
        raise ValueError('config must be an object with version=1')
    if config.get('profile') not in {'software', 'research', 'business', 'custom'}:
        raise ValueError('invalid profile')
    for key in ('sources', 'extensions', 'exclude'):
        if not isinstance(config.get(key), list) or not all(isinstance(x, str) and x for x in config[key]):
            raise ValueError(f'{key} must be a list of nonempty strings')
    if not config['sources'] or not config['extensions']:
        raise ValueError('sources and extensions cannot be empty')
    for name in config['sources']:
        path = safe(root, name)
        if path == root / '.wiki' or (root / '.wiki') in path.parents:
            raise ValueError('.wiki cannot be a source')
    if not all(re.fullmatch(r'\.[A-Za-z0-9]+', x) for x in config['extensions']):
        raise ValueError('extensions must be suffixes such as .md')
    dirs = config.get('page_dirs')
    if not isinstance(dirs, dict) or not dirs:
        raise ValueError('page_dirs must map page types to directories')
    paths = []
    for kind, name in dirs.items():
        if not re.fullmatch(r'[a-z][a-z0-9_-]*', kind):
            raise ValueError(f'invalid page type: {kind}')
        path = safe(root / '.wiki', name)
        if not PurePosixPath(name).parts or any(p.startswith('.') for p in PurePosixPath(name).parts):
            raise ValueError('page directories must be non-hidden subdirectories')
        if PurePosixPath(name).parts[0] in {'templates', 'config.json', 'index.md', 'overview.md', 'schema.md', 'purpose.md', 'log.md'}:
            raise ValueError(f'reserved page directory: {name}')
        if any(path == old or old in path.parents or path in old.parents for old in paths):
            raise ValueError('page directories must not overlap')
        paths.append(path)
    limit = config.get('max_source_bytes')
    if type(limit) is not int or limit < 1:
        raise ValueError('max_source_bytes must be a positive integer')


def context(root_arg):
    root = Path(root_arg).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError('root must be a directory')
    wiki = safe(root, '.wiki')
    config = read_json(safe(wiki, 'config.json'))
    check_config(config, root)
    return root, wiki, config


def excluded(rel, config):
    parts = PurePosixPath(rel).parts
    if any(p.startswith('.') or p in SKIP_DIRS for p in parts):
        return True
    name = parts[-1].lower() if parts else ''
    if name in {'credentials', 'credentials.json', 'secrets.json', 'secrets.yaml', 'secrets.yml'} or name.endswith(('.key', '.pem')):
        return True
    prefixes = [PurePosixPath(*parts[:i]).as_posix() for i in range(1, len(parts) + 1)]
    return any(fnmatch.fnmatchcase(prefix, p) or (p.endswith('/**') and prefix == p[:-3])
               for prefix in prefixes for p in config['exclude'])


def scan(root, config):
    files, warnings = {}, []

    def collect(path):
        rel = path.relative_to(root).as_posix()
        if excluded(rel, config) or path.suffix.lower() not in {ext.lower() for ext in config['extensions']}:
            return
        try:
            safe(root, rel)
            if path.stat().st_size > config['max_source_bytes']:
                warnings.append({'path': rel, 'reason': 'too_large'})
                return
            data = path.read_bytes()
            if len(data) > config['max_source_bytes']:
                raise ValueError('source grew beyond size limit')
            data.decode('utf-8')
            if b'\x00' in data:
                raise ValueError('binary content')
            files[rel] = {'sha256': digest(data), 'bytes': len(data)}
        except (OSError, ValueError) as exc:
            warnings.append({'path': rel, 'reason': str(exc)})

    for name in config['sources']:
        start = safe(root, name)
        if excluded(start.relative_to(root).as_posix(), config):
            warnings.append({'path': name, 'reason': 'configured_source_excluded'})
            continue
        if not start.exists():
            warnings.append({'path': name, 'reason': 'source_missing'})
        elif start.is_file():
            collect(start)
        else:
            def walk_error(exc):
                warnings.append({'path': name, 'reason': str(exc)})
            for current, dirs, names in os.walk(start, followlinks=False, onerror=walk_error):
                parent = Path(current)
                dirs[:] = sorted(d for d in dirs if not (parent / d).is_symlink() and not excluded((parent / d).relative_to(root).as_posix(), config))
                for item in sorted(names):
                    collect(parent / item)
    return {'files': dict(sorted(files.items())), 'warnings': warnings}


def frontmatter(data):
    text = data.decode('utf-8')
    match = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)', text, re.S)
    if not match:
        raise ValueError('missing JSON frontmatter between --- lines')
    try:
        meta = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise ValueError('frontmatter must use the JSON/YAML subset shown in templates') from exc
    if not isinstance(meta, dict):
        raise ValueError('frontmatter must be an object')
    return meta, text[match.end():]


def pages(wiki, config):
    result, errors = {}, []
    for kind, name in config['page_dirs'].items():
        directory = safe(wiki, name)
        if not directory.is_dir():
            errors.append(f'missing page directory: {name}')
            continue
        def walk_error(exc):
            errors.append(f'unreadable page directory: {name}: {exc}')
        for current, dirs, names in os.walk(directory, followlinks=False, onerror=walk_error):
            parent = Path(current)
            for d in dirs:
                if (parent / d).is_symlink():
                    errors.append(f'symlink in page directory: {parent / d}')
            dirs[:] = sorted(d for d in dirs if not (parent / d).is_symlink())
            for item in sorted(names):
                if not item.endswith('.md'):
                    continue
                path = parent / item
                rel = path.relative_to(wiki).as_posix()
                try:
                    safe(wiki, rel)
                    data = path.read_bytes()
                    meta, body = frontmatter(data)
                    result[rel] = {'meta': meta, 'body': body, 'sha256': digest(data), 'kind': kind}
                except (OSError, ValueError) as exc:
                    errors.append(f'{rel}: {exc}')
    return result, errors


def dependencies(page):
    refs = page['meta'].get('sources', [])
    if not isinstance(refs, list):
        return {}
    return {s['path']: s.get('sha256') for s in refs if isinstance(s, dict) and isinstance(s.get('path'), str)}


def manifest(wiki):
    path = safe(wiki, '.state/manifest.json')
    if not path.exists():
        return {'version': 1, 'pages': {}}
    data = read_json(path)
    if not isinstance(data, dict) or data.get('version') != 1 or not isinstance(data.get('pages'), dict):
        raise ValueError('invalid manifest; preserve and repair state explicitly')
    for name, entry in data['pages'].items():
        safe(wiki, name)
        if not isinstance(entry, dict) or not isinstance(entry.get('sources'), dict) or not isinstance(entry.get('sha256'), str):
            raise ValueError('invalid manifest page record')
    return data


def changes(root, wiki, config):
    sources = scan(root, config)
    content, errors = pages(wiki, config)
    prior = manifest(wiki)['pages']
    represented = set()
    impacted = []
    for name, page in content.items():
        deps = dependencies(page)
        represented.update(deps)
        reasons = []
        for path, sha in deps.items():
            actual = sources['files'].get(path)
            if actual is None:
                reasons.append({'source': path, 'reason': 'missing_excluded_or_unreadable'})
            elif actual['sha256'] != sha:
                reasons.append({'source': path, 'reason': 'source_changed'})
        if name in prior and prior[name]['sha256'] != page['sha256']:
            reasons.append({'reason': 'page_changed_since_checkpoint'})
        elif name not in prior:
            reasons.append({'reason': 'not_checkpointed'})
        if reasons:
            impacted.append({'page': name, 'reasons': reasons})
    return {'unrepresented_sources': sorted(set(sources['files']) - represented),
            'affected_pages': impacted, 'removed_pages': sorted(set(prior) - set(content)) if not errors else [],
            'unresolved_pages': sorted(set(prior) - set(content)) if errors else [],
            'warnings': sources['warnings'], 'errors': errors}


def links(text, file, root, wiki):
    # Ignore code examples; links there are not navigable content.
    text = re.sub(r'```.*?```', '', text, flags=re.S)
    text = re.sub(r'`[^`\n]*`', '', text)
    raw = [(m.group(1), False) for m in re.finditer(r'!?\[[^\]\n]*\]\(([^)\n]+)\)', text)]
    raw += [(m.group(1).split('|')[0], True) for m in re.finditer(r'\[\[([^]\n]+)\]\]', text)]
    targets, errors = [], []
    for value, wikilink in raw:
        value = value.strip()
        if value.startswith('<') and '>' in value:
            value = value[1:value.index('>')]
        else:
            value = re.split(r'\s+["\']', value, maxsplit=1)[0]
        if re.match(r'^[a-zA-Z][\w+.-]*:', value) or value.startswith('#'):
            continue
        value = unquote(value.split('#')[0])
        if not value:
            continue
        path = (wiki if wikilink else file.parent) / value
        if wikilink and not path.suffix:
            path = path.with_suffix('.md')
        normalized = Path(os.path.abspath(path))
        if not normalized.is_relative_to(root):
            errors.append(f'link escapes project: {value}')
            continue
        try:
            safe(root, normalized.relative_to(root).as_posix())
            if not normalized.is_file():
                errors.append(f'broken local link: {value}')
            else:
                targets.append(normalized)
        except ValueError as exc:
            errors.append(str(exc))
    return targets, errors


def validate(root, wiki, config):
    content, errors = pages(wiki, config)
    source = scan(root, config)
    warnings = list(source['warnings'])
    ids, graph = {}, {}
    for name, page in content.items():
        meta = page['meta']
        ident = meta.get('id')
        if not isinstance(ident, str) or not re.fullmatch(r'[a-z0-9][a-z0-9_-]*', ident):
            errors.append(f'{name}: invalid stable id')
        elif ident in ids:
            errors.append(f'{name}: duplicate id {ident}')
        else:
            ids[ident] = name
        if meta.get('type') != page['kind']:
            errors.append(f'{name}: type must match configured directory')
        if not isinstance(meta.get('title'), str) or not meta['title'].strip():
            errors.append(f'{name}: missing title')
        if meta.get('status') not in STATUSES or meta.get('freshness') not in FRESHNESS:
            errors.append(f'{name}: invalid status/freshness')
        if not isinstance(meta.get('aliases'), list) or not all(isinstance(x, str) for x in meta['aliases']):
            errors.append(f'{name}: aliases must be strings')
        if 'verified_at' not in meta or (meta['verified_at'] is not None and not isinstance(meta['verified_at'], str)):
            errors.append(f'{name}: verified_at must be a date string or null')
        refs = meta.get('sources')
        if not isinstance(refs, list) or not refs:
            errors.append(f'{name}: authored pages require sources')
            refs = []
        for ref in refs:
            if not isinstance(ref, dict) or not isinstance(ref.get('path'), str) or not re.fullmatch('[0-9a-f]{64}', str(ref.get('sha256', ''))):
                errors.append(f'{name}: invalid source reference')
                continue
            actual = source['files'].get(ref['path'])
            if actual is None:
                errors.append(f'{name}: unavailable or unconfigured source {ref["path"]}')
            elif actual['sha256'] != ref['sha256']:
                warnings.append({'page': name, 'source': ref['path'], 'reason': 'stale_source'})
        if 'REPLACE_' in page['body'] or 'REPLACE_' in json.dumps(meta):
            errors.append(f'{name}: unfinished page template')
        rels = meta.get('relations')
        if not isinstance(rels, list):
            errors.append(f'{name}: relations must be a list')
    for name, page in content.items():
        rels = page['meta'].get('relations', [])
        for rel in rels if isinstance(rels, list) else []:
            if not isinstance(rel, dict) or rel.get('type') not in RELATIONS or rel.get('target') not in ids:
                errors.append(f'{name}: invalid relation or missing target')
    documents = {wiki / name: page['body'] for name, page in content.items()}
    for name in ('purpose.md', 'schema.md', 'index.md', 'overview.md', 'log.md'):
        path = safe(wiki, name)
        if not path.is_file():
            errors.append(f'missing control: {name}')
        else:
            documents[path] = path.read_text(encoding='utf-8')
    for file, body in documents.items():
        targets, bad = links(body, file, root, wiki)
        graph[file] = targets
        errors.extend(f'{file.relative_to(wiki)}: {message}' for message in bad)
    reachable, queue = set(), [wiki / 'index.md']
    while queue:
        file = queue.pop()
        if file not in reachable:
            reachable.add(file)
            queue.extend(graph.get(file, []))
    for name in content:
        if wiki / name not in reachable:
            warnings.append({'page': name, 'reason': 'not_reachable_from_index'})
    return {'ok': not errors, 'pages': len(content), 'errors': errors, 'warnings': warnings}


def initialize(args):
    root = Path(args.root).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError('root must be a directory')
    wiki = safe(root, '.wiki')
    if wiki.exists():
        raise ValueError('.wiki already exists; inspect and migrate explicitly')
    config = read_json(Path(args.config)) if args.config else read_json(TEMPLATES / 'config.json')
    if not args.config:
        config['profile'] = args.profile
        config['sources'] = ['docs'] if args.profile == 'software' else ['.']
    check_config(config, root)
    # Validate before the first mutation; mkdir never replaces an existing Wiki.
    wiki.mkdir()
    (wiki / 'config.json').write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for name in ('purpose.md', 'schema.md', 'index.md'):
        (wiki / name).write_text((TEMPLATES / name).read_text(encoding='utf-8'), encoding='utf-8')
    (wiki / 'overview.md').write_text('# Overview\n\nInitialized framework. No sources synthesized yet.\n', encoding='utf-8')
    (wiki / 'log.md').write_text(f'# Wiki log\n\n- {datetime.now(timezone.utc).isoformat()}: initialized {config["profile"]} framework.\n', encoding='utf-8')
    (wiki / '.gitignore').write_text('.state/\n', encoding='utf-8')
    (wiki / 'templates').mkdir()
    for name in ('topic.md', 'entity.md', 'concept.md'):
        (wiki / 'templates' / name).write_text((TEMPLATES / name).read_text(encoding='utf-8'), encoding='utf-8')
    for name in config['page_dirs'].values():
        safe(wiki, name).mkdir(parents=True)
    return {'ok': True, 'wiki': str(wiki), 'profile': config['profile'], 'content_state': 'empty_framework'}


def checkpoint(root, wiki, config, names, forgotten=None):
    forgotten = forgotten or []
    if not names and not forgotten:
        raise ValueError('checkpoint requires --page or --forget-page')
    content, errors = pages(wiki, config)
    if errors:
        raise ValueError('; '.join(errors))
    selected = {}
    sources = scan(root, config)['files']
    for name in forgotten:
        if safe(wiki, name).exists():
            raise ValueError(f'cannot forget an existing page: {name}')
    for name in names:
        safe(wiki, name)
        if name not in content:
            raise ValueError(f'not a configured page: {name}')
        page = content[name]
        deps = dependencies(page)
        if not deps or len(deps) != len(page['meta'].get('sources', [])):
            raise ValueError(f'{name}: source references missing or duplicated')
        for path, sha in deps.items():
            if path not in sources or sources[path]['sha256'] != sha:
                raise ValueError(f'{name}: source changed, unavailable or unconfigured: {path}')
        selected[name] = {'sha256': page['sha256'], 'sources': deps}
    state = safe(wiki, '.state')
    state.mkdir(exist_ok=True)
    lock = safe(wiki, '.state/checkpoint.lock')
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ValueError('checkpoint lock exists; inspect active writer before explicit recovery') from exc
    temporary = None
    try:
        os.close(descriptor)
        data = manifest(wiki)
        for name in forgotten:
            if safe(wiki, name).exists():
                raise ValueError(f'page reappeared before checkpoint: {name}')
            data['pages'].pop(name, None)
        # Recheck the exact bytes immediately before publishing the checkpoint.
        for name, entry in selected.items():
            if digest(safe(wiki, name).read_bytes()) != entry['sha256']:
                raise ValueError(f'page changed during checkpoint: {name}')
            for path, sha in entry['sources'].items():
                if digest(safe(root, path).read_bytes()) != sha:
                    raise ValueError(f'source changed during checkpoint: {path}')
        data['pages'].update(selected)
        data['updated_at'] = datetime.now(timezone.utc).isoformat()
        with tempfile.NamedTemporaryFile(mode='w', dir=state, encoding='utf-8', delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write('\n')
        os.replace(temporary, safe(wiki, '.state/manifest.json'))
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        lock.unlink()
    return {'ok': True, 'checkpointed': sorted(selected), 'forgotten': sorted(forgotten)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('init', 'scan', 'search', 'diff', 'validate', 'checkpoint'):
        command = sub.add_parser(name)
        command.add_argument('--root', required=True)
        if name == 'init':
            command.add_argument('--profile', choices=['software', 'research', 'business', 'custom'], default='custom')
            command.add_argument('--config', help='Prepared JSON config; overrides all profile defaults')
        elif name == 'search':
            command.add_argument('--query', required=True)
            command.add_argument('--limit', type=int, default=5)
        elif name == 'checkpoint':
            command.add_argument('--page', action='append', default=[])
            command.add_argument('--forget-page', action='append', default=[], help='Acknowledge an intentionally removed page; never deletes content')
    args = parser.parse_args(argv)
    try:
        if args.command == 'init':
            result = initialize(args)
        else:
            root, wiki, config = context(args.root)
            if args.command == 'scan':
                result = scan(root, config)
            elif args.command == 'diff':
                result = changes(root, wiki, config)
            elif args.command == 'validate':
                result = validate(root, wiki, config)
            elif args.command == 'checkpoint':
                result = checkpoint(root, wiki, config, args.page, args.forget_page)
            else:
                if not 1 <= args.limit <= 50 or not args.query.strip():
                    raise ValueError('query must be nonempty; limit must be 1..50')
                content, errors = pages(wiki, config)
                terms = list(dict.fromkeys(args.query.casefold().split()))
                hits = []
                for name, page in content.items():
                    searchable = json.dumps(page['meta'], ensure_ascii=False) + '\n' + page['body']
                    score = sum(searchable.casefold().count(term) for term in terms)
                    if score:
                        lines = [line.strip() for line in searchable.splitlines() if any(term in line.casefold() for term in terms)]
                        hits.append({'page': name, 'title': page['meta'].get('title'), 'score': score, 'snippet': '\n'.join(lines[:3])[:800]})
                result = {'hits': sorted(hits, key=lambda x: (-x['score'], x['page']))[:args.limit], 'errors': errors, 'freshness_checked': False}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result.get('errors') or result.get('ok') is False else 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    sys.exit(main())
