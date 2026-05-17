---
name: link-fetcher
description: Batch-fetch a list of URLs and save them as local files. arXiv links (abs/html/pdf) are downloaded as PDF files; all other URLs are fetched via Jina Reader and saved as Markdown. Failed URLs are reported in a summary. Trigger this skill when the user provides a list of links (or a file containing links) and wants the content saved locally for offline reading or further processing.
---

# Link Fetcher

## Overview

Fetch a batch of URLs and persist their content locally.
- **arXiv links** (abs / html / pdf) → downloaded as `.pdf`
- **All other URLs** → fetched via Jina Reader (`https://r.jina.ai/<url>`) and saved as `.md`
- **Failures** → recorded in `failed.txt` inside the output directory

## Workflow

### Step 1 — Collect URLs

Accept URLs from the user in any of these forms:
- Inline in the conversation (one per line, or as a list)
- A local text file path (one URL per line, `#` lines are comments)
- From an existing document (e.g. a `doc.md` reference list)

Extract only the bare URLs; strip labels like `[1]`, `[2]`, parenthetical text, etc.

### Step 2 — Determine output directory

Ask the user for an output directory if not specified, or default to `./fetched_output` relative to the current working directory.

### Step 3 — Run the fetch script

Execute the bundled script:

```bash
# From a list of inline URLs
python3 <skill-dir>/scripts/fetch_links.py \
  --urls "https://..." "https://..." \
  --output-dir ./fetched_output

# From a text file
python3 <skill-dir>/scripts/fetch_links.py \
  --file urls.txt \
  --output-dir ./fetched_output
```

`<skill-dir>` is the directory where this skill is installed (e.g. `~/.claude/skills/link-fetcher`).

### Step 4 — Report results

After the script finishes, report to the user:
- Total URLs processed
- Number of successes (with output filenames)
- Number of failures (with reasons, also written to `failed.txt`)

### Step 5 — Handle failures

For any failed URLs, suggest alternatives:
- **arXiv PDF failed** → try the `/abs/` page via Jina Reader as fallback
- **Jina returned empty** → note the URL is likely behind a hard paywall or login wall
- **HTTP 4xx/5xx** → note the URL may be dead or geo-restricted

## URL Routing Rules

| URL pattern | Action |
|---|---|
| `arxiv.org/abs/*` | Convert to `arxiv.org/pdf/<id>`, download PDF |
| `arxiv.org/pdf/*` | Download PDF directly |
| `arxiv.org/html/*` | Convert to `arxiv.org/pdf/<id>`, download PDF |
| `*.pdf` (direct PDF link) | Download PDF directly |
| Everything else | Fetch via Jina Reader → save as `.md` |

## Output Structure

```
fetched_output/
├── arxiv_org_pdf_2308_03688.pdf
├── arxiv_org_pdf_2602_03238.pdf
├── arize_com_blog_what_is_an_agent_harness.md
├── anthropic_com_research_bloom.md
├── ...
└── failed.txt          ← only created if there are failures
```

## Scripts

- `scripts/fetch_links.py` — main fetch script (stdlib only, no pip dependencies)

## Notes

- The script uses only Python standard library (`urllib`, `pathlib`, `re`) — no installation needed.
- A 0.5-second delay is inserted between requests to avoid rate-limiting.
- Filenames are derived from the URL and truncated to 100 characters.
- arXiv version suffixes (e.g. `v1`) are stripped for clean PDF URLs.
