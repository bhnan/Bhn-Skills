---
name: wiki-creator
description: >
  Initialize a personal, domain-specific Wiki knowledge base project with the standard
  directory structure, purpose.md, schema.md, guide.md, and page templates. Use this skill
  whenever a user wants to create a Wiki, knowledge base, or second brain for a specific
  topic — especially when they say things like "create a wiki for X", "build a knowledge
  base about Y", "help me organize my notes on Z", or "set up a personal wiki". This skill
  is specifically designed for *narrow, personal* domains (e.g., "LLM Reasoning" not "AI";
  "Byzantine History" not "History"). Always trigger this skill when the user wants to
  scaffold a new wiki project, even if they just say "new wiki" or "init wiki".
---

# Wiki Creator Skill

This skill scaffolds a personal, domain-specific Wiki project designed to be written and
maintained entirely by LLMs. It guides the user through a structured interview to define
the wiki's scope, then generates the full directory structure with all necessary files.

## Core Philosophy

A good wiki is **narrow and personal**:
- ❌ "Machine Learning" → ✅ "LLM Reasoning Techniques"
- ❌ "History" → ✅ "Byzantine Military History 500–1000 AD"
- ❌ "Productivity" → ✅ "Deep Work Strategies for Solo Founders"

The wiki is *yours* — it reflects your questions, not a textbook's table of contents.
You curate sources and ask questions; the LLM does the filing, cross-referencing, and
bookkeeping.

---

## Phase 1: Domain Scoping Interview

Before generating any files, have a conversation to surface:
1. The exact domain (specific enough to fill one bookshelf, not a library)
2. The user's **personal angle** (why *they* care, what *they* want to answer)
3. The core recurring entities and concepts
4. Naming conventions

### Fast Path vs Full Interview

**If the user already gave you substantial detail** (domain + entity types + personal angle),
extract what you can from the conversation, fill gaps with reasonable defaults, then jump
straight to the Confirmation Summary below. Don't re-ask things they already answered.

**If the user gave you only a topic name**, run the full interview — but do it as a
natural conversation, not a form. Weave the questions together; don't number them aloud.
A good first message covers domain + personal angle in one go:

> "Tell me a bit more about what you want to track here — what specific questions are
> you trying to answer, and what's drawing you to this area? Also, what kinds of things
> keep coming up that you'd want pages for — researchers, papers, specific techniques?"

#### Key things to establish:

**Domain scope** — Push back if too broad. The test: *could one expert read everything
important in this domain in 6–12 months?* If not, narrow further.

> "That sounds like it could fill a library. What's your specific angle on [topic]?
> For example, 'AI' might mean 'prompt engineering' or 'LLM reasoning' or 'RLHF' —
> which slice is yours?"

**Personal Key Questions** — These go into `purpose.md`. Help the user make them
concrete. "Understand X better" is too vague; push toward "What causes X to happen
in Y context?" or "How does technique A differ from B in practice?"

**Entity & Concept types** — Group what they name into:
- **Entities** (concrete, named things): people, papers, models, orgs, datasets
- **Concepts** (abstract ideas): techniques, frameworks, phenomena, debates

Aim for 2–4 of each. If they struggle, suggest defaults from `references/domain-patterns.md`.

**Naming conventions** — Pick a pattern and commit; don't leave as TBD.
Common choices: `Lastname_Firstname` for people, `ShortTitle_Year` for papers.

---

### Confirmation Summary (required before generating)

After the interview, always produce a brief summary for the user to confirm:

> **Here's what I've got:**
> - **Domain:** [specific name]
> - **Out of scope:** [2–3 exclusions]
> - **Key Questions:** [3–5 bullet points]
> - **Entities:** [type list]
> - **Concepts:** [type list]
> - **Naming:** [convention summary]
>
> Does this capture it correctly? Anything to adjust?

Only proceed to Phase 2 after the user confirms.

---

## Phase 2: Generate Files

Once the user confirms, immediately generate all files and directories. No further preview
or confirmation needed — tell the user where the wiki was created and it's ready to use.

**Important:** The goal of this phase is to build the framework, not fill in content.
- `purpose.md`, `schema.md`, `guide.md` — fill these in fully using information from the interview
- `wiki/` files (`index.md`, `log.md`, `overview.md`) — generate as **stubs only** with placeholder text; do NOT fill in any domain knowledge
- `wiki/docs/`, `wiki/entities/`, `wiki/concepts/` — create empty directories only
- All actual wiki content is added later through ingest operations, not during initialization

### Directory Structure to Create

```
{wiki-name}/
├── purpose.md
├── schema.md
├── guide.md                        ← LLM operation guide for this wiki
├── raw/
│   ├── sources/                    ← drop source documents here
│   └── assets/
├── wiki/
│   ├── index.md
│   ├── log.md
│   ├── overview.md
│   ├── docs/                       ← comprehensive topic articles (flat, no subdirs)
│   ├── entities/
│   │   └── {type}/                 ← one subdir per entity type from schema
│   └── concepts/
│       └── {type}/                 ← one subdir per concept type from schema
├── templates/
│   ├── entity_page.md
│   ├── concept_page.md
│   └── doc.md
├── .obsidian/
│   └── app.json
└── .llm-wiki/
    ├── config.json
    └── audit.log
```

### File Templates

#### `purpose.md`
```markdown
# Wiki Purpose: {Domain Name}

## Mission
{1–2 sentences: what this wiki is and why it exists}

## Scope
**In scope:** {list 3–5 things that belong here}
**Out of scope:** {list 2–3 things explicitly excluded — critical for staying narrow}

## Key Questions
{3–7 questions the user personally wants to answer, written in first person}
1. ...
2. ...

## Success Criteria
{What would it mean for this wiki to be "working"? What will the user be able to do?}

## Owner
{User's name or "Anonymous"} — created {date}
```

#### `schema.md`

Generate this file as real Markdown (not a code block). It defines the domain structure
that guides LLM navigation and organization across all operations.

```
# Wiki Schema: {Domain Name}

## Page Types

### Entity Pages (wiki/entities/)
Entities are named, concrete things that recur across the domain.
They function as a dictionary — concise definitions that link to relevant docs.

For each entity type:

#### {EntityType} (entities/{type}/)
- **Definition:** {what counts as this entity type}
- **Naming convention:** {pattern} (e.g., Lastname_Firstname, ShortTitle_Year)
- **Required frontmatter fields:** type, aliases, tags, plus any domain-specific fields
- **Example filename:** {example}.md

### Concept Pages (wiki/concepts/)
Concepts are abstract ideas, techniques, or frameworks.
They function as a dictionary — concise definitions that link to relevant docs.
(Same structure as Entity Pages above, adapted for concepts)

### Doc Pages (wiki/docs/)
Comprehensive articles on topics, workflows, or analyses. Each doc synthesizes
knowledge from one or more sources and represents accumulated understanding on a
specific subject. This is the primary content layer of the wiki.

## Linking Conventions
- Internal links use [[Page_Name]] syntax (Obsidian-compatible)
- Every doc page must reference its source file(s): [[raw/sources/filename]]
- Entity and concept pages should link to related doc pages
- Cross-type links are encouraged: docs link to entities and concepts

## Tagging Convention
{Define 3–6 top-level tags for the domain, e.g. #foundational, #recent, #contested}

## Naming Rules
{Summarize all naming decisions from the interview in one place}
```

#### `guide.md`

Generate as real Markdown, filled in with this wiki's specific details. This file tells
any LLM how to operate on this wiki. Always read `wiki/index.md` first before any operation.

```
# Wiki Guide: {Domain Name}

This wiki is maintained by LLMs. This guide defines how to perform all standard operations.

## Directory Overview

| Path | Purpose |
|---|---|
| `wiki/index.md` | Master navigation — always read first |
| `wiki/docs/` | Comprehensive topic articles (primary content) |
| `wiki/entities/{type}/` | Entity dictionary: {entity types} |
| `wiki/concepts/{type}/` | Concept dictionary: {concept types} |
| `raw/sources/` | Original source documents (read-only) |
| `wiki/log.md` | Append-only operation log |
| `schema.md` | Domain structure and naming conventions |
| `templates/` | Page templates for creating new pages |

## Operations

### Query
To answer a question about this wiki:
1. Read `wiki/index.md` to identify relevant pages
2. Read `schema.md` to understand domain structure and terminology
3. Read the relevant doc, entity, and concept pages
4. Synthesize an answer with citations to specific wiki pages
5. If the answer represents valuable new knowledge, save it as a new doc in `wiki/docs/`
   following `templates/doc.md`

### Update / Ingest
When new source material arrives or knowledge needs to be added:
1. Read `wiki/index.md` and `schema.md` to understand the current state of the wiki
2. Identify which existing pages are related to the new content
3. Check for conflicts with existing content:
   - **Conflict found:** update the relevant pages to resolve it, log in `wiki/log.md`
   - **Already covered:** skip — don't create duplicate content
   - **New knowledge:** create a new doc in `wiki/docs/` following `templates/doc.md`
4. Update any relevant entity or concept pages
5. Update `wiki/index.md` to include any new pages
6. Append an entry to `wiki/log.md`

Every doc page must reference its source file(s) in `raw/sources/`.

### Lint
Periodically health-check the wiki:
1. Find contradictions between pages — flag and resolve
2. Find orphan pages — pages not linked from `wiki/index.md`
3. Find stale content — claims that newer sources have superseded
4. Find missing pages — entities or concepts mentioned in docs but lacking their own page
5. Find missing cross-references — pages that should link to each other but don't
6. Output a lint report summarizing findings and recommended actions
```

#### `wiki/index.md`
```markdown
# {Domain} Wiki — Index

> Maintained by LLM. Updated on every ingest operation.

## Docs
{Sections linking to wiki/docs/ pages, organized by the domain's key themes}

## Entities
{Sections per entity type, linking to wiki/entities/{type}/ pages}

## Concepts
{Sections per concept type, linking to wiki/concepts/{type}/ pages}

_Last updated: {date}_
```

#### `wiki/overview.md`
```markdown
# {Domain} — Overview

> Initialized: {date}. Maintained by LLM — updated as the wiki grows.

## What This Wiki Is About
_To be filled in as content accumulates._

## Current State of the Field
_To be filled in after first ingest operations._

## Open Questions
_See purpose.md for initial key questions. Updated here as understanding evolves._

## Key Themes
_To be identified as patterns emerge across docs._
```

#### `wiki/log.md`
```markdown
# Operation Log

> Append-only. Each entry records a discrete LLM operation on this wiki.
> Recommended format: `## [YYYY-MM-DD] {operation} | {brief description}`

---

## [{date}] init | Wiki Initialized
- Created directory structure
- Defined purpose and schema
- Operator: wiki-creator skill
```

#### `templates/doc.md`
```markdown
---
title: {Title}
created: {date}
updated: {date}
sources: []
tags: []
---

# {Title}

## Summary
{2–3 sentences: what this doc covers and why it matters in the context of this wiki}

## {Main Section}
{Comprehensive content — this is the primary knowledge artifact. Write in depth,
synthesizing across sources. Use additional H2 sections as needed.}

## Related
- Entities: [[entities/{type}/{name}]]
- Concepts: [[concepts/{type}/{name}]]
- Docs: [[docs/{related-doc}]]

## Sources
- [[raw/sources/{filename}]]
```

#### `templates/entity_page.md`
```markdown
---
type: {entity-type}
aliases: []
tags: []
---

# {Entity Name}

## Definition
{1–2 sentences: what this entity is}

## Key Attributes
{Domain-specific fields relevant to this entity type}

## Role in Domain
{How this entity connects to the domain's key questions and themes}

## Related
- Concepts: [[concepts/{type}/{name}]]
- Docs: [[docs/{relevant-doc}]]

## Sources
- [[raw/sources/{filename}]]
```

#### `templates/concept_page.md`
```markdown
---
type: {concept-type}
aliases: []
tags: []
---

# {Concept Name}

## Definition
{1–2 sentences: what this concept means in this domain}

## Context
{Why this concept matters, how it arose, what problem it addresses}

## Related
- Entities: [[entities/{type}/{name}]]
- Concepts: [[concepts/{type}/{name}]]
- Docs: [[docs/{relevant-doc}]]

## Sources
- [[raw/sources/{filename}]]
```

#### `.llm-wiki/config.json`
```json
{
  "wiki_name": "{domain-slug}",
  "display_name": "{Domain Name}",
  "created": "{ISO date}",
  "schema_version": "1.0",
  "entity_types": ["{type1}", "{type2}"],
  "concept_types": ["{type1}", "{type2}"],
  "obsidian_compatible": true
}
```

#### `.obsidian/app.json`
```json
{
  "legacyEditor": false,
  "livePreview": true,
  "defaultViewMode": "source"
}
```

---

## Common Pitfalls to Avoid

| Pitfall | How to Avoid |
|---|---|
| Domain too broad | Enforce the "one bookshelf" test; refuse to proceed until scoped |
| Schema has only 1 entity type | Push for at least 2; single-type wikis collapse into flat lists |
| No "out of scope" defined | Always ask what's explicitly excluded — as important as scope |
| Naming convention not decided | Don't leave it as "TBD" — pick a default and make it explicit |
| Key Questions are vague | Rewrite "understand X" as "What causes X to happen in Y context?" |

---

## Reference Files

- `references/domain-patterns.md` — Common entity/concept patterns by domain type
  (read when user's domain is in: ML/AI, history, biology, software, economics, philosophy)
