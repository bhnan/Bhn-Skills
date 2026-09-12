# Lint

```bash
python3 '<skill>/scripts/wiki.py' validate --root '<project>'
python3 '<skill>/scripts/wiki.py' diff --root '<project>'
```

Validation checks controls, JSON frontmatter, stable IDs, types, source membership/hashes, relation targets/types, local link paths and index reachability. It checks file existence, not Markdown anchor correctness or truth of claims. Diff exposes uncovered sources and prior-checkpoint changes. Cache absence is recoverable and does not invalidate knowledge.

Add editorial checks scoped to the request: contradictory conclusions, duplicate topics, ambiguous relation direction, unsupported lifecycle status, sources supporting only part of a claim, and outdated overview/index summaries. Do not claim exhaustive contradiction detection from mechanical checks.

Report errors, freshness/coverage warnings and recommended changes separately. Lint is read-only unless the user also asks to fix findings. For fixes use ingest/sync and preserve existing user edits.
