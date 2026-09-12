# Local contracts v1

Configuration is `.wiki/config.json`, UTF-8 JSON, to avoid third-party YAML dependencies. `version` is 1; `profile` is software/research/business/custom; `sources` lists project-relative directories or files; `extensions` lists readable text suffixes; `exclude` lists project-relative glob patterns; `page_dirs` maps arbitrary page types to unique non-overlapping Wiki-relative directories. `max_source_bytes` bounds one file. Sources cannot escape the project or traverse symbolic links. Hidden source directories and secret-like filenames are skipped by default. Explicitly extract permitted content into a regular configured source if necessary.

All source paths are relative to the project. All `--page` arguments are relative to `.wiki`. Page directories cannot occupy `.state`, templates, or hidden paths. Config/schema/pages may be versioned; `.state/` is ignored by generated `.wiki/.gitignore`. No Git commands are required.

Markdown frontmatter is a JSON object between `---` lines. JSON is a YAML subset; the helper accepts this subset only and reports regular YAML as unsupported. This deliberately keeps the helper dependency-free. Use the supplied templates:

```markdown
---
{
  "id": "orders-idempotency",
  "type": "topic",
  "title": "订单幂等",
  "aliases": ["重复回调"],
  "status": "implemented",
  "freshness": "fresh",
  "verified_at": "2026-09-12",
  "sources": [{"path": "docs/001-orders/spec.md", "sha256": "<64 hex characters>", "anchor": "幂等规则"}],
  "relations": [{"type": "depends_on", "target": "payment-events"}]
}
---
```

Allowed status: proposed, accepted, implemented, released, superseded, unknown. Research/business may use accepted for a supported working conclusion; do not invent delivery stages. Freshness: fresh, stale, unknown. `verified_at` may be null for unverified knowledge. Freshness is recomputed by hashes for diagnostics; author metadata alone is not proof.

Relation types: related, describes, depends_on, implements, verified_by, supersedes. Targets are page IDs, not paths. Source objects require exact path/hash; anchor is optional. Original-source links in the body use relative Markdown links from the page file. Controls (index, overview, purpose, schema, log) do not require page frontmatter.

The manifest is a reconstructible checkpoint of selected page hashes and their source dependencies, never a second content authority. Losing it removes checkpoint history, while page frontmatter still supports dependency and freshness detection. Corrupt state produces an explicit error; preserve it before repairing via a deliberate maintenance action.

Use standard relative Markdown links. The helper resolves simple inline links and Wiki links to existing project files, but does not validate heading anchors, embedded HTML or reference-style links. Avoid Wikilinks in custom layouts unless their paths are explicit from `.wiki`.
