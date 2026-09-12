# Software profile

Start from existing project documents and requested questions. Suggested entities: modules, services, interfaces; concepts: domain rules, design tradeoffs. Use project-specific names and add types only when needed.

When using ai-native-sdlc outputs, read the installed skill if available; do not hardcode the author's machine path. Current integration recognizes docs/<requirement>/intent.md, spec.md, plan.md and optional change.md. Existing differently organized artifacts can be mapped explicitly. If the skill is unavailable, inspect actual documents and disclose inferred lifecycle rules.

Intent gives scope; spec gives designed behavior; plan gives implementation and verification progress. An incomplete plan's changes belong to that requirement's three documents. After explicit full completion, accepted change.md entries amend its baseline. Proposed, failed and deferred changes do not redefine behavior. Newer requirements may reference frozen older requirements without rewriting them. Select ownership by explicit context or unambiguous directory sequence, not modification time.

Wiki synthesis must consider applicable accepted change.md entries alongside the baseline; otherwise it can resurrect obsolete behavior. Completion never proves deployment authorization. Link tests, independent review, release and incident evidence where present; do not fabricate standard filenames for them.

Current work still reads its governing spec/plan or change record. Wiki retrieval reduces irrelevant historical reading; it does not replace delivery gates or become their approval authority.
