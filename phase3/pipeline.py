"""
Phase 3.3: Pipeline — Single entry: query → retrieve → generate → answer + citation + last_updated.
Detects scheme from query (e.g. "HDFC Silver ETF") and prefers that scheme's chunks.
When GROQ_API_KEY or XAI_API_KEY is set in .env, uses that LLM (Groq preferred) for answer generation.
"""

import json
import os
import re
import sys
from pathlib import Path

# Project root so phase3.* imports resolve
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load .env from project root so XAI_API_KEY is available
_env_file = PROJECT_ROOT / ".env"
if _env_file.exists():
    for line in _env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip().strip("'\"")
            if k:
                os.environ.setdefault(k, v)

from phase3.retrieve import load_chunks, retrieve
from phase3.generate import generate_answer

SOURCES_PATH = PROJECT_ROOT / "phase1" / "sources.json"


def _load_schemes() -> list[dict]:
    """Load scheme_pages from phase1/sources.json."""
    if not SOURCES_PATH.exists():
        return []
    try:
        with open(SOURCES_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("scheme_pages") or []
    except Exception:
        return []


def get_scheme_info(scheme_id: str | None) -> dict | None:
    """Return { scheme_name, url } for the given scheme_id, or None."""
    if not scheme_id:
        return None
    for s in _load_schemes():
        if s.get("scheme_id") == scheme_id:
            return {"scheme_name": s.get("scheme_name"), "url": s.get("url")}
    return None


def detect_scheme_id(query: str) -> str | None:
    """
    If the query mentions a known scheme (by name or id), return its scheme_id.
    Enables specific answers like "Expense ratio of HDFC Silver ETF?" or "risk for silver-based fund".
    """
    schemes = _load_schemes()
    if not schemes:
        return None
    q = re.sub(r"[^\w\s]", " ", query.lower()).split()
    q_set = set(w for w in q if len(w) > 1)
    best_id, best_score = None, 0
    for s in schemes:
        name = (s.get("scheme_name") or "").lower()
        sid = (s.get("scheme_id") or "").lower()
        name_words = set(re.sub(r"[^\w\s]", " ", name).split())
        id_words = set(sid.replace("-", " ").split())
        scheme_words = name_words | id_words
        match = len(q_set & scheme_words)
        if match >= 2 and match > best_score:
            best_score = match
            best_id = s.get("scheme_id")
    if best_id:
        return best_id
    # Single-word match: use it if that word uniquely identifies one scheme (e.g. "silver" -> HDFC Silver ETF FoF)
    for w in q_set:
        matches = [
            s for s in schemes
            if w in (s.get("scheme_name") or "").lower() or w in (s.get("scheme_id") or "").replace("-", " ")
        ]
        if len(matches) == 1:
            return matches[0].get("scheme_id")
    return None


def run_pipeline(
    query: str,
    top_k: int = 5,
    scheme_id: str | None = None,
    llm_call=None,
    chunks_path: str | Path | None = None,
) -> dict:
    """
    Run full RAG pipeline. Returns { "answer", "citation_url", "last_updated", "refused" }.
    If scheme_id is None, tries to detect from query (e.g. "HDFC Silver ETF FoF").
    If GROQ_API_KEY is set, uses Groq (Llama); else if XAI_API_KEY is set, uses Grok. Otherwise chunk-only.
    chunks_path: optional path to all_chunks.jsonl (used by Streamlit so chunks are found regardless of cwd).
    """
    if scheme_id is None:
        scheme_id = detect_scheme_id(query)
    scheme_info = get_scheme_info(scheme_id)
    chunks = load_chunks(chunks_path)
    retrieved = retrieve(query, chunks=chunks, top_k=top_k, scheme_id=scheme_id)
    if llm_call is None:
        if os.environ.get("GROQ_API_KEY"):
            try:
                from phase3.llm_groq import make_llm_call
                llm_call = make_llm_call()
            except Exception:
                pass
        if llm_call is None and os.environ.get("XAI_API_KEY"):
            try:
                from phase3.llm_grok import make_llm_call
                llm_call = make_llm_call()
            except Exception:
                pass
    return generate_answer(
        query,
        retrieved,
        llm_call=llm_call,
        detected_scheme_id=scheme_id,
        scheme_info=scheme_info,
    )


if __name__ == "__main__":
    import sys as _sys
    q = _sys.argv[1] if len(_sys.argv) > 1 else "What is Riskometer?"
    result = run_pipeline(q)
    print("Answer:", result["answer"])
    print("Citation:", result["citation_url"])
    print("Last updated:", result["last_updated"])
