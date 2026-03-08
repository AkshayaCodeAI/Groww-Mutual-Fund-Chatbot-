"""
Phase 3.1: Retrieve — Load chunks and return top-k by relevance.
Reads data/chunks/all_chunks.jsonl. Optional scheme filter. Returns source_url, last_updated.
Scores by keywords in text, field, and scheme_name; boosts field/scheme-specific matches.
"""

import json
import re
from pathlib import Path

# Project root (folder containing phase3, data, etc.)
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CHUNKS_PATH = DATA_DIR / "chunks" / "all_chunks.jsonl"

# Query phrases -> chunk field (for boosting the right chunk for specific questions)
FIELD_HINTS = [
    ("expense ratio", "expense_ratio"),
    ("expense of", "expense_ratio"),
    ("expense for", "expense_ratio"),
    ("expense", "expense_ratio"),
    ("exit load", "exit_load"),
    ("min one time sip", "min_1st_investment"),
    ("minimum one time sip", "min_1st_investment"),
    ("one time sip min", "min_1st_investment"),
    ("one time sip", "min_1st_investment"),
    ("one time investment", "min_1st_investment"),
    ("minimum sip", "min_sip"),
    ("min sip", "min_sip"),
    ("sip for", "min_sip"),
    ("sip of", "min_sip"),
    ("sip amount", "min_sip"),
    ("minimum lump", "min_lumpsum"),
    ("min lump", "min_lumpsum"),
    ("lumpsum", "min_lumpsum"),
    ("lump sum", "min_lumpsum"),
    ("riskometer", "riskometer_meaning"),
    ("level of risk", "risk"),
    ("risk associated", "risk"),
    ("risk is", "risk"),
    ("risk level", "risk"),
    ("risk for", "risk"),
    ("risk of", "risk"),
    ("risk", "risk"),
    ("nav", "nav_meaning"),
    ("net asset value", "nav_meaning"),
    ("lock in", "lock_in_period"),
    ("lock-in", "lock_in_period"),
    ("benchmark", "benchmark"),
    ("fund manager", "fund_manager"),
    ("launch date", "launch_date"),
    ("category", "category"),
    ("scheme type", "scheme_type"),
    ("top holdings", "top_holdings"),
    ("holdings", "top_holdings"),
    ("returns", "return_1y"),
    ("1 year", "return_1y"),
    ("3 year", "return_3y"),
    ("5 year", "return_5y"),
    ("elss", "elss_tax_benefit"),
    ("tax", "ltcg_tax_rule"),
    ("ltcg", "ltcg_tax_rule"),
    ("stcg", "stcg_tax_rule"),
    ("download statement", "how_to_download_statement"),
    ("capital gains", "how_to_download_capital_gains_report"),
    ("kyc", "how_to_update_kyc"),
]


def load_chunks(chunks_path: Path | str | None = None) -> list[dict]:
    """Load all chunks from JSONL. Include glossary (already merged by phase2).
    If chunks_path is provided, load from that file (for Streamlit/deploy when cwd may differ)."""
    path = Path(chunks_path) if chunks_path else CHUNKS_PATH
    chunks = []
    if not path.exists():
        return chunks
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))
    return chunks


def _query_field_hint(query_lower: str) -> str | None:
    """Return the chunk field that best matches the query, or None."""
    for phrase, field in FIELD_HINTS:
        if phrase in query_lower:
            return field
    return None


def retrieve(
    query: str,
    chunks: list[dict] | None = None,
    top_k: int = 5,
    scheme_id: str | None = None,
) -> list[dict]:
    """
    Retrieve top-k chunks relevant to query. Keyword scoring over text, field, and scheme_name.
    If scheme_id is set, prefer chunks for that scheme. Boosts field-specific and scheme-specific matches.
    Returns list of { "text", "source_url", "last_updated", "scheme_name" }.
    """
    if chunks is None:
        chunks = load_chunks()
    q_lower = query.lower()
    words = re.sub(r"[^\w\s]", " ", q_lower).split()
    stop = {"what", "is", "the", "a", "an", "of", "for", "to", "in", "on", "how", "do", "does", "can"}
    q_words = set(w for w in words if len(w) > 1 and w not in stop)
    if not q_words:
        q_words = set(w for w in words if len(w) > 1)
    if "minimum" in q_words:
        q_words.add("min")
    if "lumpsum" in q_words or "lump" in q_words:
        q_words.add("lumpsum")
        q_words.add("lump")

    query_field = _query_field_hint(q_lower)

    def score(c: dict) -> float:
        text = (c.get("text") or "").lower()
        field = (c.get("field") or "").lower()
        scheme_name = (c.get("scheme_name") or "").lower()
        searchable = f"{text} {field} {scheme_name}"
        c_scheme = c.get("scheme_id")
        if scheme_id and c_scheme is not None and c_scheme != scheme_id:
            return -1.0
        s = sum(1 for w in q_words if w in searchable)
        if scheme_id and c_scheme == scheme_id:
            s += 3
        if query_field and field == query_field:
            s += 4
        if ("sip" in q_words or "min" in q_words) and "minimum" in q_lower and field == "min_sip":
            s += 3
        if ("lump" in q_words or "lumpsum" in q_words) and "minimum" in q_lower and field == "min_lumpsum":
            s += 3
        return float(s)

    scored = [(score(c), c) for c in chunks]
    scored = [(s, c) for s, c in scored if s >= 0]
    scored.sort(key=lambda x: (-x[0], x[1].get("scheme_id") or ""))
    selected = [c for _, c in scored[:top_k]]

    return [
        {
            "text": c.get("text", ""),
            "source_url": c.get("source_url", ""),
            "last_updated": c.get("last_updated", ""),
            "scheme_name": c.get("scheme_name"),
            "field": c.get("field"),
            "scheme_id": c.get("scheme_id"),
        }
        for c in selected
    ]
