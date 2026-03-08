"""
Phase 2.3: Chunk — Build RAG chunks from parsed JSON + glossary.
Reads phase1/glossary_chunks.json and data/parsed/*.json; writes data/chunks/all_chunks.jsonl.
Ensures every chunk has a non-empty source_url so answers always have a proper citation link.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # project root
PHASE1_DIR = ROOT / "phase1"
DATA_DIR = ROOT / "data"
PARSED_DIR = DATA_DIR / "parsed"
CHUNKS_DIR = DATA_DIR / "chunks"
GLOSSARY_PATH = PHASE1_DIR / "glossary_chunks.json"
HOWTO_PATH = PHASE1_DIR / "howto_chunks.json"
SOURCES_PATH = PHASE1_DIR / "sources.json"

DEFAULT_GLOSSARY_URL = "https://groww.in/mutual-funds"
DEFAULT_HELP_URL = "https://groww.in/help"

SCHEME_FIELDS = (
    "type", "expense_ratio", "exit_load", "min_sip", "min_lumpsum", "lock_in_period",
    "benchmark", "risk", "fund_manager", "launch_date", "category", "scheme_type",
    "return_1y", "return_3y", "return_5y", "elss_tax_benefit", "ltcg_tax_rule", "stcg_tax_rule",
    "tax_implication", "stamp_duty", "fund_house", "fund_house_url", "about_scheme", "investment_objective",
    "min_1st_investment", "min_2nd_investment", "one_time_sip", "holding_analysis", "advanced_ratios",
    "asset_allocation",
    "annualised_returns_definition", "absolute_returns_definition", "expense_ratio_definition",
    "exit_load_definition", "stamp_duty_definition", "tax_definition",
)


def _chunk(scheme_id: str, scheme_name: str, source_url: str, last_updated: str, field: str, value) -> dict | None:
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
    elif isinstance(value, list):
        if not value:
            return None
        if value and isinstance(value[0], dict):
            parts = []
            for item in value:
                name = item.get("name") or item.get("Name") or ""
                assets = item.get("assets") or item.get("Assets") or ""
                if name or assets:
                    parts.append(f"{name}: {assets}".strip())
            text = "\n".join(parts[:20]) if parts else None
        else:
            text = ", ".join(str(x) for x in value[:20])
        if not text:
            return None
    else:
        text = str(value)
    if not text or len(text) > 8000:
        text = text[:8000] if text else None
    if not text:
        return None
    return {
        "text": text,
        "scheme_id": scheme_id,
        "scheme_name": scheme_name,
        "source_url": source_url,
        "field": field,
        "last_updated": last_updated,
    }


def _get_scheme_url(scheme_id: str) -> str:
    """Return scheme page URL from sources.json for scheme_id; else default MF page."""
    if not SOURCES_PATH.exists():
        return DEFAULT_GLOSSARY_URL
    try:
        with open(SOURCES_PATH, encoding="utf-8") as f:
            data = json.load(f)
        for s in data.get("scheme_pages") or []:
            if s.get("scheme_id") == scheme_id:
                return s.get("url") or DEFAULT_GLOSSARY_URL
    except Exception:
        pass
    return DEFAULT_GLOSSARY_URL


def build_chunks_for_scheme(data: dict) -> list[dict]:
    scheme_id = data.get("scheme_id", "")
    scheme_name = data.get("scheme_name", "")
    source_url = (data.get("source_url") or "").strip() or _get_scheme_url(scheme_id)
    last_updated = data.get("last_updated", "")
    chunks = []
    for key in SCHEME_FIELDS:
        val = data.get(key)
        c = _chunk(scheme_id, scheme_name, source_url, last_updated, key, val)
        if c:
            if key in ("expense_ratio", "min_sip", "min_lumpsum", "exit_load"):
                label = {"min_sip": "Minimum SIP", "min_lumpsum": "Minimum lump sum", "expense_ratio": "Expense ratio", "exit_load": "Exit load"}.get(key, key.replace("_", " ").title())
                c["text"] = f"{label}: {c['text']}"
            chunks.append(c)
    holdings = data.get("top_holdings") or []
    if holdings:
        lines = ["Top holdings:"]
        for h in holdings[:15]:
            name = h.get("name") or h.get("Name") or ""
            assets = h.get("assets") or h.get("Assets") or ""
            lines.append(f"  {name}: {assets}")
        c = _chunk(scheme_id, scheme_name, source_url, last_updated, "top_holdings", "\n".join(lines))
        if c:
            chunks.append(c)
    for faq in data.get("faqs") or []:
        q = faq.get("question") or faq.get("q")
        a = faq.get("answer") or faq.get("a")
        if q and a:
            c = _chunk(scheme_id, scheme_name, source_url, last_updated, "faq", f"Q: {q}\nA: {a}")
            if c:
                chunks.append(c)
    return chunks


def load_glossary_chunks() -> list[dict]:
    if not GLOSSARY_PATH.exists():
        return []
    with open(GLOSSARY_PATH, encoding="utf-8") as f:
        items = json.load(f)
    return [
        {
            "text": g.get("text", ""),
            "scheme_id": g.get("scheme_id"),
            "scheme_name": g.get("scheme_name"),
            "source_url": (g.get("source_url") or "").strip() or DEFAULT_GLOSSARY_URL,
            "field": g.get("topic", "glossary"),
            "last_updated": g.get("last_updated", ""),
        }
        for g in items if g.get("text")
    ]


def load_howto_chunks() -> list[dict]:
    """Load how-to chunks (download statement, capital gains report, update KYC)."""
    if not HOWTO_PATH.exists():
        return []
    with open(HOWTO_PATH, encoding="utf-8") as f:
        items = json.load(f)
    return [
        {
            "text": h.get("text", ""),
            "scheme_id": h.get("scheme_id"),
            "scheme_name": h.get("scheme_name"),
            "source_url": (h.get("source_url") or "").strip() or DEFAULT_HELP_URL,
            "field": h.get("topic", "howto"),
            "last_updated": h.get("last_updated", ""),
        }
        for h in items if h.get("text")
    ]


def run_build_chunks() -> None:
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    all_chunks = []
    if not PARSED_DIR.exists():
        PARSED_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(PARSED_DIR.glob("*.json")):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        chunks = build_chunks_for_scheme(data)
        all_chunks.extend(chunks)
        print(f"  {path.name}: {len(chunks)} chunks")
    glossary = load_glossary_chunks()
    all_chunks.extend(glossary)
    if glossary:
        print(f"  glossary: {len(glossary)} chunks")
    howto = load_howto_chunks()
    all_chunks.extend(howto)
    if howto:
        print(f"  howto: {len(howto)} chunks")
    out_file = CHUNKS_DIR / "all_chunks.jsonl"
    with open(out_file, "w", encoding="utf-8") as f:
        for c in all_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"Wrote {len(all_chunks)} chunks -> {out_file}")


if __name__ == "__main__":
    run_build_chunks()
    print("Done.")
