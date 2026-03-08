"""
Validate scraped/chunk data and pipeline: every chunk has a proper source_url,
and sample questions return answers with proper citation links.
Run from project root: python3 -m phase2.validate_data
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CHUNKS_PATH = DATA_DIR / "chunks" / "all_chunks.jsonl"

VALID_PREFIXES = ("https://groww.in/", "http://groww.in/")


def validate_chunks() -> tuple[bool, list[str]]:
    """Check every chunk has non-empty source_url pointing to Groww. Returns (ok, errors)."""
    errors = []
    if not CHUNKS_PATH.exists():
        return False, [f"Chunks file not found: {CHUNKS_PATH}. Run: python3 -m phase2.chunk"]
    chunks = []
    with open(CHUNKS_PATH, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                c = json.loads(line)
                chunks.append(c)
            except json.JSONDecodeError as e:
                errors.append(f"Line {i}: invalid JSON - {e}")
                continue
            url = (c.get("source_url") or "").strip()
            if not url:
                errors.append(f"Line {i}: chunk field={c.get('field')} has empty source_url")
            elif not url.startswith(VALID_PREFIXES):
                errors.append(f"Line {i}: chunk field={c.get('field')} source_url not Groww: {url[:60]}")
    return len(errors) == 0, errors


def validate_pipeline_links() -> tuple[bool, list[str]]:
    """Run sample queries and check each response has a proper citation_url. Returns (ok, errors)."""
    try:
        from phase3.pipeline import run_pipeline
    except ImportError:
        return False, ["Cannot import phase3.pipeline (run from project root)"]

    test_cases = [
        "What is Riskometer?",
        "What is NAV?",
        "Minimum SIP for SBI Gold Fund?",
        "How to download statement?",
        "Expense ratio of HDFC Silver ETF FoF?",
    ]
    errors = []
    for q in test_cases:
        try:
            r = run_pipeline(q)
        except Exception as e:
            errors.append(f"Query '{q[:40]}...': pipeline error - {e}")
            continue
        url = (r.get("citation_url") or "").strip()
        if not url:
            errors.append(f"Query '{q[:50]}': response has no citation_url")
        elif not url.startswith(VALID_PREFIXES):
            errors.append(f"Query '{q[:50]}': citation_url not Groww: {url[:60]}")
    return len(errors) == 0, errors


def main() -> int:
    print("Validating chunk data (source_url in every chunk)...")
    ok1, err1 = validate_chunks()
    if ok1:
        print("  OK: All chunks have valid source_url.")
    else:
        for e in err1:
            print("  ERROR:", e)
    print()
    print("Validating pipeline (citation link in answers for sample questions)...")
    ok2, err2 = validate_pipeline_links()
    if ok2:
        print("  OK: Sample queries return answers with proper citation links.")
    else:
        for e in err2:
            print("  ERROR:", e)
    print()
    if ok1 and ok2:
        print("All validations passed.")
        return 0
    print("Some validations failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
