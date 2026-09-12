# Initialize

Read [contracts](contracts.md). Inspect existing documentation locations, filenames and a small representative sample. If `.wiki` already exists, inspect it and propose/adapt changes within the user's request; never run initialization over it. An unrelated legacy `wiki/` is not an invitation to move files.

Recover scope, intended questions and sources from the conversation. Ask only for missing choices that materially affect the result. Offer defaults from one profile: [software](profiles/software.md), [research](profiles/research.md), [business](profiles/business.md), or [custom](profiles/custom.md). Profiles are defaults, not fixed ontologies.

Prepare the customized config as a JSON file using the Agent's file editing tool, outside the not-yet-created `.wiki`. Show consequential assumptions while proceeding within the user's authorization. Configure source roots, extensions, excludes and page directories. Never include generated `.wiki` as a source. Use the config template as a starting point.

```bash
python3 '<skill>/scripts/wiki.py' init --root '<project>' --profile software --config '<prepared-config.json>'
```

Omit `--config` to use defaults; software defaults to `docs`, other scenes to `.`. The helper refuses existing `.wiki`, seeds controls and copies page templates into `.wiki/templates`. Fill purpose, schema and index in the user's language. Extend local templates for custom types; do not edit the installed skill for one project's ontology.

The initialized index/overview are explicit empty-state stubs. If the user requested a framework only, stop after validation. If they requested a Wiki based on supplied materials, continue through ingest and author useful pages; scaffolding alone does not complete that request. Missing/unreadable sources must be disclosed, not described as empty knowledge.

Do not create AGENTS.md by default. If an explicit project-entry integration is requested, append a short pointer with demand conditions, preserving all existing rules. Do not include mandatory index-first for unrelated work.
