"""
Phase 2.1: Scrape — Fetch HTML from Groww scheme pages.
Reads phase1/sources.json; saves to data/raw_pages/*.html.
"""

import json
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]  # project root (folder containing phase1, phase2, data)
PHASE1_DIR = ROOT / "phase1"
DATA_DIR = ROOT / "data"
SOURCES_PATH = PHASE1_DIR / "sources.json"
RAW_DIR = DATA_DIR / "raw_pages"

FETCH_DELAY = 1.5
REQUEST_TIMEOUT = 30.0
USER_AGENT = "GrowwMFBot/1.0 (FAQ chatbot; facts-only)"


def load_sources() -> dict:
    with open(SOURCES_PATH, encoding="utf-8") as f:
        return json.load(f)


def fetch_url(url: str, delay_after: float = 0) -> str:
    with httpx.Client(
        follow_redirects=True,
        timeout=REQUEST_TIMEOUT,
        headers={"User-Agent": USER_AGENT},
    ) as client:
        resp = client.get(url)
        resp.raise_for_status()
        html = resp.text
    if delay_after > 0:
        time.sleep(delay_after)
    return html


def scrape_scheme_pages() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    sources = load_sources()
    for scheme in sources["scheme_pages"]:
        scheme_id = scheme["scheme_id"]
        url = scheme["url"]
        out_file = RAW_DIR / f"{scheme_id}.html"
        print(f"Fetching {scheme_id}...")
        try:
            html = fetch_url(url, delay_after=FETCH_DELAY)
            out_file.write_text(html, encoding="utf-8")
            print(f"  Saved {len(html)} chars -> {out_file.name}")
        except httpx.HTTPStatusError as e:
            print(f"  HTTP error: {e.response.status_code}")
        except Exception as e:
            print(f"  Error: {e}")


def scrape_help_pages() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    sources = load_sources()
    for help_page in sources.get("help_pages", []):
        url = help_page["url"]
        uid = help_page.get("id", "help")
        out_file = RAW_DIR / f"{uid}.html"
        print(f"Fetching help: {uid}...")
        try:
            html = fetch_url(url, delay_after=FETCH_DELAY)
            out_file.write_text(html, encoding="utf-8")
            print(f"  Saved -> {out_file.name}")
        except Exception as e:
            print(f"  Error: {e}")


if __name__ == "__main__":
    scrape_scheme_pages()
    scrape_help_pages()
    print("Done.")
