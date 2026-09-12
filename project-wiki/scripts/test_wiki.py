"""Behavioral checks using disposable workspaces; no user project is modified."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import wiki

SCRIPT = Path(__file__).with_name('wiki.py')


class WikiTests(unittest.TestCase):
    def setUp(self):
        # Keep failed fixtures inspectable; never clear a pre-existing directory.
        self.root = Path(tempfile.mkdtemp(prefix='project-wiki-test-')).resolve()
        (self.root / 'docs').mkdir()
        (self.root / 'docs/a.md').write_text('# Orders\n\n订单回调必须幂等。\n', encoding='utf-8')
        (self.root / 'docs/b.md').write_text('# Other\n\nIndependent topic.\n', encoding='utf-8')
        self.cli('init', '--profile', 'software')

    def cli(self, command, *args, code=0):
        result = subprocess.run([sys.executable, str(SCRIPT), command, '--root', str(self.root), *args], text=True, capture_output=True)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def page(self, name='a', source='docs/a.md', kind='topic', directory='topics'):
        sha = hashlib.sha256((self.root / source).read_bytes()).hexdigest()
        meta = dict(id=name, type=kind, title='订单幂等 ' + name, aliases=['重复回调'], status='accepted', freshness='fresh', verified_at='2026-09-12', sources=[dict(path=source, sha256=sha)], relations=[])
        path = self.root / '.wiki' / directory / (name + '.md')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('---\n' + json.dumps(meta, ensure_ascii=False) + '\n---\n\n# 订单幂等\n\n来源支持幂等约束。\n', encoding='utf-8')
        index = self.root / '.wiki/index.md'
        index.write_text(index.read_text() + f'\n[{name}]({directory}/{name}.md)\n')
        return path

    def snapshot(self):
        return {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}

    def test_init_and_duplicate_preserves_files(self):
        self.assertTrue(self.cli('validate')['ok'])
        before = self.snapshot()
        self.cli('init', code=2)
        self.assertEqual(before, self.snapshot())
        self.assertFalse((self.root / 'AGENTS.md').exists())
        self.assertFalse((self.root / '.git').exists())

    def test_read_only_query_and_scan(self):
        self.page()
        before = self.snapshot()
        self.assertEqual(len(self.cli('scan')['files']), 2)
        self.assertEqual(self.cli('search', '--query', '重复回调')['hits'][0]['page'], 'topics/a.md')
        self.cli('diff')
        self.cli('validate')
        self.assertEqual(before, self.snapshot())
        self.assertFalse((self.root / '.wiki/.state').exists())

    def test_incremental_changes_and_stale_checkpoint(self):
        self.page()
        self.page('b', 'docs/b.md')
        self.cli('checkpoint', '--page', 'topics/a.md', '--page', 'topics/b.md')
        self.assertEqual(self.cli('diff')['affected_pages'], [])
        (self.root / 'docs/a.md').write_text('# Revised\nNew rule.\n')
        diff = self.cli('diff')
        self.assertEqual([x['page'] for x in diff['affected_pages']], ['topics/a.md'])
        self.cli('checkpoint', '--page', 'topics/a.md', code=2)
        self.assertTrue(any(w['reason'] == 'stale_source' for w in self.cli('validate')['warnings']))
        self.page()
        self.cli('checkpoint', '--page', 'topics/a.md')
        self.assertEqual(self.cli('diff')['affected_pages'], [])

    def test_deleted_source_and_cache_rebuild(self):
        self.page()
        self.cli('checkpoint', '--page', 'topics/a.md')
        (self.root / '.wiki/.state/manifest.json').rename(self.root / '.wiki/.state/manifest.saved')
        self.assertEqual(self.cli('diff')['affected_pages'][0]['reasons'][0]['reason'], 'not_checkpointed')
        (self.root / 'docs/a.md').rename(self.root / 'docs/a.old')
        self.assertEqual(self.cli('diff')['affected_pages'][0]['reasons'][0]['reason'], 'missing_excluded_or_unreadable')
        self.cli('validate', code=1)

    def test_custom_type_layout(self):
        path = self.root / '.wiki/config.json'
        config = json.loads(path.read_text())
        config['profile'] = 'custom'
        config['page_dirs'] = {'customer': 'business/customers'}
        path.write_text(json.dumps(config))
        self.page(kind='customer', directory='business/customers')
        self.assertTrue(self.cli('validate')['ok'])
        self.cli('checkpoint', '--page', 'business/customers/a.md')
        self.assertEqual(self.cli('search', '--query', '订单')['hits'][0]['page'], 'business/customers/a.md')

    def test_symlink_source_and_state(self):
        (self.root / 'docs/link.md').symlink_to(self.root / 'docs/a.md')
        scan = self.cli('scan')
        self.assertNotIn('docs/link.md', scan['files'])
        self.page()
        outside = Path(tempfile.mkdtemp(prefix='wiki-outside-'))
        (self.root / '.wiki/.state').symlink_to(outside)
        self.cli('checkpoint', '--page', 'topics/a.md', code=2)
        self.assertEqual(list(outside.iterdir()), [])

    def test_exclusion_and_path_escape(self):
        (self.root / 'docs/.env').write_text('secret')
        path = self.root / '.wiki/config.json'
        config = json.loads(path.read_text())
        config['exclude'].append('docs/b.md')
        path.write_text(json.dumps(config))
        self.assertEqual(list(self.cli('scan')['files']), ['docs/a.md'])
        config['sources'] = ['../']
        path.write_text(json.dumps(config))
        self.cli('scan', code=2)

    def test_relation_link_and_template_validation(self):
        page = self.page()
        text = page.read_text().replace('"relations": []', '"relations": [{"type":"depends_on","target":"absent"}]')
        page.write_text(text + '\n[broken](missing.md)\n')
        result = self.cli('validate', code=1)
        self.assertTrue(any('relation' in x for x in result['errors']))
        self.assertTrue(any('broken local link' in x for x in result['errors']))

    def test_explicit_excluded_source_and_uppercase_extension(self):
        private = self.root / 'docs/private'
        private.mkdir()
        (private / 'secret.md').write_text('excluded material')
        path = self.root / '.wiki/config.json'
        config = json.loads(path.read_text())
        config.update(sources=['docs/private'], exclude=['docs/private'])
        path.write_text(json.dumps(config))
        self.assertEqual(self.cli('scan')['files'], {})
        config.update(sources=['docs/private/secret.md'])
        path.write_text(json.dumps(config))
        self.assertEqual(self.cli('scan')['files'], {})
        config.update(sources=['docs'], extensions=['.MD'])
        path.write_text(json.dumps(config))
        self.assertEqual(len(self.cli('scan')['files']), 2)

    def test_page_metadata_and_hash_share_snapshot(self):
        target = self.page()
        original = target.read_bytes()
        config = json.loads((self.root / '.wiki/config.json').read_text())
        reads = []
        real_read = Path.read_bytes
        def changing_read(path):
            if path == target:
                reads.append(path)
                return original if len(reads) == 1 else b'new conflicting page'
            return real_read(path)
        with patch.object(Path, 'read_bytes', changing_read):
            result, errors = wiki.pages(self.root / '.wiki', config)
        self.assertEqual(errors, [])
        self.assertEqual(len(reads), 1)
        self.assertEqual(result['topics/a.md']['sha256'], hashlib.sha256(original).hexdigest())

    def test_unreadable_page_tree_not_reported_deleted(self):
        self.page()
        self.cli('checkpoint', '--page', 'topics/a.md')
        config = json.loads((self.root / '.wiki/config.json').read_text())
        real_walk = wiki.os.walk
        def unreadable(top, *args, **kwargs):
            if Path(top) == self.root / '.wiki/topics':
                kwargs['onerror'](PermissionError('fixture denied'))
                return iter(())
            return real_walk(top, *args, **kwargs)
        with patch.object(wiki.os, 'walk', unreadable):
            result = wiki.changes(self.root, self.root / '.wiki', config)
        self.assertTrue(result['errors'])
        self.assertEqual(result['removed_pages'], [])
        self.assertEqual(result['unresolved_pages'], ['topics/a.md'])

    def test_explicit_removed_page_acknowledgement(self):
        target = self.page()
        self.cli('checkpoint', '--page', 'topics/a.md')
        self.cli('checkpoint', '--forget-page', 'topics/a.md', code=2)
        target.rename(target.with_suffix('.saved'))
        self.assertEqual(self.cli('diff')['removed_pages'], ['topics/a.md'])
        self.cli('checkpoint', '--forget-page', 'topics/a.md')
        self.assertEqual(self.cli('diff')['removed_pages'], [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
