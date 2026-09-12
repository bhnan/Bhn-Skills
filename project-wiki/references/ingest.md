# Ingest

Read [contracts](contracts.md), local config, purpose and schema. Use index and focused search to identify canonical homes before adding pages. Avoid reading unrelated profiles. Software-specific status questions may require its profile and the available ai-native-sdlc skill.

```bash
python3 '<skill>/scripts/wiki.py' scan --root '<project>'
```

Use the selected paths and SHA-256 values as input evidence. Read the actual selected source before authoring. Scan lists bounded text sources; PDFs, audio, images and remote URLs need a separately available extraction tool and a local readable derivative with original provenance. Do not rename binary files to make them ingestible. Report excluded or unreadable material.

Organize around stable questions and concepts. One source can affect multiple pages; a page can synthesize multiple sources. Prefer updating the canonical page over duplicates. Use local templates. Fill the JSON frontmatter contract and source path/hash at the time read. Include source links and relevant section anchors in prose. Record inferred relations as qualified claims, not established facts.

Do not copy whole original documents. Do not treat assistant speculation, a plan checkbox, or an unverified test claim as durable verified knowledge. Conflicts retain their competing sources and unresolved status. AI-Native SDLC records remain authoritative for delivery gates.

Update affected entity/concept pages, navigation and a concise dated log. Generated prose uses the user's language. Record `verified_at` only for evidence actually checked. `freshness` describes content/source correspondence, independently of delivery status.

```bash
python3 '<skill>/scripts/wiki.py' validate --root '<project>'
python3 '<skill>/scripts/wiki.py' checkpoint --root '<project>' --page 'topics/example.md'
```

Repeat `--page` for all newly written or updated pages. Checkpoint refuses source hashes that no longer match; reread and revise affected content, then retry. It records synchronization, not semantic approval. Never refresh a source hash without examining whether the associated claim changed.

Run diff after writing and disclose remaining uncovered/stale sources. Initial creation is complete when the requested scope has useful linked content; do not demand that every repository file has a page.
