# Domain Patterns Reference

Common entity and concept type patterns by domain category.
Use these as suggestions when the user struggles to name their schema types.

---

## ML / AI Research

**Entity types (pick 2–4):**
- `papers` — research papers, preprints
- `models` — named model architectures (GPT-4, Claude, Mistral)
- `researchers` — individual authors / labs
- `datasets` — named benchmarks or training corpora
- `organizations` — labs, companies, funding bodies

**Concept types (pick 2–4):**
- `techniques` — specific algorithmic methods (e.g., RLHF, LoRA, RAG)
- `phenomena` — observed behaviors (e.g., emergent abilities, hallucination)
- `frameworks` — theoretical lenses (e.g., scaling laws, mechanistic interp)
- `metrics` — evaluation approaches (e.g., BLEU, MMLU, ELO)

**Example narrow domains:**
- "LLM Reasoning" → researchers + papers + techniques + phenomena
- "Mechanistic Interpretability" → papers + models + researchers + techniques + phenomena
- "RLHF & Alignment" → papers + researchers + techniques + datasets + phenomena

---

## History

**Entity types:**
- `people` — historical figures
- `events` — battles, treaties, crises
- `places` — cities, regions, empires
- `texts` — primary source documents, chronicles

**Concept types:**
- `themes` — historiographical arguments
- `periods` — defined time spans with characteristics
- `movements` — intellectual or political currents

---

## Biology / Medicine

**Entity types:**
- `species` / `organisms`
- `genes` / `proteins`
- `studies` — landmark papers or trials
- `researchers`

**Concept types:**
- `mechanisms` — biochemical or physiological processes
- `hypotheses` — contested scientific claims
- `techniques` — lab or clinical methods

---

## Software / Engineering

**Entity types:**
- `tools` — named software, libraries, CLIs
- `systems` — architectures, platforms
- `people` — key contributors, authors
- `orgs` — companies, open-source communities

**Concept types:**
- `patterns` — design or architectural patterns
- `tradeoffs` — known engineering tensions
- `techniques` — implementation approaches

---

## Philosophy

**Entity types:**
- `philosophers` — thinkers
- `texts` — books, papers, dialogues
- `schools` — named philosophical traditions

**Concept types:**
- `arguments` — specific named arguments or proofs
- `positions` — stances on a question (e.g., compatibilism)
- `problems` — open or classic questions (e.g., problem of evil)
- `distinctions` — conceptual pairs or clarifications

---

## Economics / Finance

**Entity types:**
- `economists` — researchers
- `papers` / `books`
- `institutions` — central banks, think tanks
- `markets` / `instruments`

**Concept types:**
- `models` — formal economic models
- `phenomena` — observed economic behaviors
- `policies` — named policy approaches
- `debates` — contested empirical or normative questions
