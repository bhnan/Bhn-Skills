# Synchronize

Read [contracts](contracts.md) and local configuration. This is explicit maintenance; a normal query does not start it.

```bash
python3 '<skill>/scripts/wiki.py' diff --root '<project>'
```

Use changed/deleted dependencies and new unrepresented sources to select work. The report combines page frontmatter with prior checkpoints, so missing cache cannot make existing stale pages fresh. If a page changed externally, inspect that edit before authoring. Read only affected sources/pages and the relationships needed to assess downstream claims.

Apply [ingest](ingest.md) to the affected subset. A renamed/deleted source needs evidence reconciliation, not blind deletion of knowledge. Preserve historical conclusions with a valid retained source or clearly mark unsupported material. Missing configured roots or unreadable sources are availability failures; do not infer factual retractions from them.

For concurrent work, capture target content before drafting and recheck immediately before patching. If it changed, merge with that edit or defer the page. Never overwrite another author's work. The helper checks source fingerprints at checkpoint and serializes checkpoint writers, but cannot make Agent-authored multi-file edits atomic.

Update index/log, validate, and checkpoint only processed pages. Untouched stale pages remain stale in diff. Repeated sync without source changes should not manufacture pages or rewrite timestamps. Report coverage gaps separately from invalid links and outdated claims.

After an explicitly intended page removal or relocation, acknowledge the absent old path with `checkpoint --root '<project>' --forget-page 'topics/old.md'`. This removes only that checkpoint record, never content, and refuses existing paths. Update incoming links and checkpoint the new page first. Do not acknowledge removal when traversal errors make a page merely unavailable; diff reports those paths as unresolved.

No scheduling, daemon, semantic merge automation or cloud integration is implemented by this version.
