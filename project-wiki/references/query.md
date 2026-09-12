# Query

If no `.wiki/config.json` exists, say no project Wiki is available and use source files within the request; do not create one. Read config to locate custom page directories.

For a whole-project introduction, start with `.wiki/index.md` and `.wiki/overview.md`. For a specific question, search directly:

```bash
python3 '<skill>/scripts/wiki.py' search --root '<project>' --query '订单 幂等' --limit 5
```

The helper searches configured page directories including hidden `.wiki`, titles, aliases and page contents. Queries use literal whitespace-separated terms, not regex. Chinese terms should be selected deliberately; this is lexical matching, not semantic retrieval. Default budget: two searches and three relevant pages. Stop early when evidence is sufficient; exceed only when a concrete unresolved question warrants it.

Inspect matching sections and source references. Retrieve linked original sections to substantiate decisions or current behavior. If needed read schema for relation meanings. Relations are directed and need evidence; `related` alone does not prove dependency.

`diff` can expose source drift; a successful search is not a freshness check. If sources changed, qualify old knowledge and read live sources. Cite paths and headings, distinguish historical from current conclusions. A miss means coverage/search may be insufficient, not that no decision exists. Fall back to a targeted source search, explaining the gap.

No query command changes files, repairs indexes, checkpoints state or triggers workers. Do not persist new answers unless the user asks to ingest them. With no Git, use source hashes exactly as in Git projects.
