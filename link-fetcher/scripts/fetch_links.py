#!/usr/bin/env python3
"""
fetch_links.py — Batch URL fetcher for link-fetcher skill.

Usage:
    python fetch_links.py --urls "url1" "url2" ...
    python fetch_links.py --file urls.txt
    python fetch_links.py --file urls.txt --output-dir ./doc

Output directory defaults to ./doc/YYYY-MM-DD/

Routing:
    - URL ends with .pdf           → download as PDF directly
    - arxiv.org (abs/html/pdf)     → convert to PDF URL, download (retry up to 3x)
    - Everything else              → Jina Reader → save as .md (title-named)
    - Failures                     → listed in failed.txt

Requires: pip install requests
"""

import argparse
import os
import re
import sys
import time
import requests
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


# ──────────────────────────────────────────────
# .env loader
# ──────────────────────────────────────────────

def load_env(env_file: Path | None = None) -> dict[str, str]:
    env: dict[str, str] = {}
    candidates = [env_file] if env_file else [
        Path.cwd() / ".env",
        Path(__file__).parent.parent / ".env",
    ]
    for path in candidates:
        if path and path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, _, v = line.partition("=")
                    env[k.strip()] = v.strip()
            break
    return env


# ──────────────────────────────────────────────
# Unified HTTP fetch
# ──────────────────────────────────────────────

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Mozilla/5.0 (compatible; link-fetcher/1.0)"})


def http_get(url: str, timeout: int = 30, retries: int = 1,
             extra_headers: dict | None = None) -> tuple[bytes | None, str]:
    """Fetch URL, return (content_bytes, error_message). Retries with exponential backoff."""
    headers = dict(extra_headers) if extra_headers else {}
    for attempt in range(retries):
        try:
            resp = SESSION.get(url, headers=headers, timeout=timeout)
            resp.raise_for_status()
            return resp.content, ""
        except Exception as e:
            if attempt < retries - 1:
                wait = 2 ** attempt
                print(f"    retry {attempt + 1}/{retries - 1} after {wait}s ({e})")
                time.sleep(wait)
            else:
                return None, str(e)
    return None, "unknown error"


# ──────────────────────────────────────────────
# URL classification
# ──────────────────────────────────────────────

def is_direct_pdf(url: str) -> bool:
    return urlparse(url).path.lower().endswith(".pdf")


def is_arxiv(url: str) -> bool:
    return "arxiv.org" in url


def arxiv_to_pdf_url(url: str) -> str:
    match = re.search(r"arxiv\.org/(?:abs|pdf|html)/([0-9]+\.[0-9]+)", url)
    if match:
        return f"https://arxiv.org/pdf/{match.group(1)}"
    return re.sub(r"/(abs|html)/", "/pdf/", url)


def strip_trailing_slash(url: str) -> str:
    parsed = urlparse(url)
    if parsed.path not in ("", "/") and parsed.path.endswith("/"):
        return url.rstrip("/")
    return url


# ──────────────────────────────────────────────
# Filename helpers
# ──────────────────────────────────────────────

def title_to_filename(title: str, ext: str) -> str:
    title = re.sub(r"[^\w\s\-]", "", title)
    title = re.sub(r"\s+", "_", title.strip())
    return f"{title[:80]}{ext}"


def url_to_filename(url: str, ext: str) -> str:
    parsed = urlparse(url)
    name = (parsed.netloc + parsed.path).replace("/", "_")
    name = re.sub(r"[^\w\-]", "_", name)[:80]
    return f"{name}{ext}"


def extract_title(markdown: str) -> str | None:
    for line in markdown.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
        if line.lower().startswith("title:"):
            return line[6:].strip()
    return None


def unique_path(dest: Path) -> Path:
    if not dest.exists():
        return dest
    stem, suffix = dest.stem, dest.suffix
    i = 2
    while True:
        candidate = dest.with_name(f"{stem}_{i}{suffix}")
        if not candidate.exists():
            return candidate
        i += 1


# ──────────────────────────────────────────────
# Fetch handlers
# ──────────────────────────────────────────────

def handle_pdf(url: str, output_dir: Path, retries: int = 1) -> tuple[bool, str]:
    content, err = http_get(url, retries=retries)
    if content is None:
        return False, err
    if len(content) < 1000:
        return False, f"Response too small ({len(content)} bytes), likely not a PDF"
    dest = unique_path(output_dir / url_to_filename(url, ".pdf"))
    dest.write_bytes(content)
    print(f"  ✓ PDF  → {dest.name}")
    return True, ""


def handle_jina(url: str, output_dir: Path, api_key: str = "") -> tuple[bool, str]:
    clean_url = strip_trailing_slash(url)
    jina_url = f"https://r.jina.ai/{clean_url}"
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else None
    content, err = http_get(jina_url, extra_headers=headers)
    if content is None:
        return False, err
    text = content.decode("utf-8", errors="replace").strip()
    if len(text) < 100:
        return False, f"Jina returned near-empty content ({len(text)} chars)"
    title = extract_title(text)
    filename = title_to_filename(title, ".md") if title else url_to_filename(url, ".md")
    dest = unique_path(output_dir / filename)
    dest.write_text(text, encoding="utf-8")
    print(f"  ✓ MD   → {dest.name}")
    return True, ""


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def process_urls(urls: list[str], output_dir: Path, jina_api_key: str = "") -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []
    clean_urls = [u.strip() for u in urls if u.strip() and not u.strip().startswith("#")]

    for i, url in enumerate(clean_urls, 1):
        print(f"[{i}/{len(clean_urls)}] {url}")

        if is_direct_pdf(url):
            ok, err = handle_pdf(url, output_dir, retries=1)
        elif is_arxiv(url):
            pdf_url = arxiv_to_pdf_url(url)
            ok, err = handle_pdf(pdf_url, output_dir, retries=3)
            if not ok:
                err = f"PDF URL: {pdf_url}\n  Error: {err}"
        else:
            ok, err = handle_jina(url, output_dir, api_key=jina_api_key)

        if not ok:
            print(f"  ✗ Failed: {err}")
            failures.append(f"{url}\n  {err}")

        time.sleep(0.5)

    fail_file = output_dir / "failed.txt"
    if failures:
        fail_file.write_text(
            f"Failed URLs ({len(failures)} total)\n{'=' * 40}\n\n"
            + "\n\n".join(failures) + "\n",
            encoding="utf-8",
        )
        print(f"\n⚠️  {len(failures)} URL(s) failed → {fail_file}")
    else:
        print("\n✅ All URLs processed successfully.")

    print(f"📊 {len(clean_urls) - len(failures)}/{len(clean_urls)} succeeded  →  {output_dir}")


def main():
    today = date.today().strftime("%Y-%m-%d")
    parser = argparse.ArgumentParser(description="Batch URL fetcher")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--urls", nargs="+", metavar="URL")
    src.add_argument("--file", metavar="FILE")
    parser.add_argument("--output-dir", "-o", default=f"./doc/{today}")
    parser.add_argument("--env", metavar="FILE", help=".env file path (default: auto-detect)")
    args = parser.parse_args()

    env = load_env(Path(args.env) if args.env else None)
    jina_api_key = os.environ.get("JINA_API_KEY") or env.get("jina_api_key", "")
    if jina_api_key:
        print("🔑 Jina API key loaded")

    if args.urls:
        urls = args.urls
    else:
        path = Path(args.file)
        if not path.exists():
            print(f"Error: file not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        urls = path.read_text(encoding="utf-8").splitlines()

    process_urls(urls, Path(args.output_dir), jina_api_key=jina_api_key)


if __name__ == "__main__":
    main()
