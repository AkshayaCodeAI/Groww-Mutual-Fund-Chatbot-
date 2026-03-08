"""
Phase 3.2: Generate — Produce answer from retrieved chunks with constraints.
Facts-only; refusal for advice/opinion and return comparisons; ≤3 sentences; one citation.
"""

import sys
from pathlib import Path

# Project root so "from phase3.config.prompts" resolves
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from phase3.config.prompts import (
    SYSTEM_PROMPT,
    REFUSAL_MESSAGE,
    EDUCATIONAL_LINK,
    REFUSAL_TRIGGERS,
    COMPARISON_REFUSAL_TRIGGERS,
    COMPARISON_REFUSAL_MESSAGE,
    RETURNS_REFUSAL_TEMPLATE,
)


def is_refusal_query(query: str) -> bool:
    q = query.lower().strip()
    return any(t in q for t in REFUSAL_TRIGGERS)


def is_comparison_query(query: str) -> bool:
    """Refuse requests for comparison of schemes (e.g. 'comparison of all schemes')."""
    q = query.lower().strip()
    return any(t in q for t in COMPARISON_REFUSAL_TRIGGERS)


def is_returns_comparison(query: str) -> bool:
    q = query.lower()
    return "return" in q and ("compare" in q or " vs " in q or "versus" in q or "which" in q)


def format_context(retrieved: list[dict]) -> str:
    parts = []
    for i, r in enumerate(retrieved, 1):
        url = r.get("source_url", "")
        text = r.get("text", "")
        parts.append(f"[Source {i}]({url}):\n{text}")
    return "\n\n".join(parts)


def generate_answer(
    query: str,
    retrieved: list[dict],
    llm_call=None,
    detected_scheme_id: str | None = None,
    scheme_info: dict | None = None,
) -> dict:
    """
    Returns { "answer", "citation_url", "last_updated", "refused" }.
    If llm_call is None, uses first chunk text as fallback (no API key needed).
    When scheme_info is provided and the best chunk is generic (no scheme_id), appends
    a scheme-specific link so the user gets one clear citation to the scheme page.
    """
    citation_url = ""
    last_updated = ""
    if retrieved:
        citation_url = retrieved[0].get("source_url", "")
        last_updated = retrieved[0].get("last_updated", "")

    if is_refusal_query(query):
        return {
            "answer": REFUSAL_MESSAGE,
            "citation_url": EDUCATIONAL_LINK,
            "last_updated": last_updated or "N/A",
            "refused": True,
        }

    if is_comparison_query(query):
        return {
            "answer": COMPARISON_REFUSAL_MESSAGE,
            "citation_url": EDUCATIONAL_LINK,
            "last_updated": last_updated or "N/A",
            "refused": True,
        }

    if is_returns_comparison(query) and citation_url:
        return {
            "answer": RETURNS_REFUSAL_TEMPLATE.format(citation_url=citation_url),
            "citation_url": citation_url,
            "last_updated": last_updated or "N/A",
            "refused": True,
        }

    if not retrieved:
        if scheme_info and scheme_info.get("url"):
            return {
                "answer": "No relevant facts were found in our sources for this question. For scheme-specific details, see the link below.",
                "citation_url": scheme_info["url"],
                "last_updated": "N/A",
                "refused": False,
            }
        return {
            "answer": "No relevant facts were found in our sources for this question. For general information on mutual funds, see the link below.",
            "citation_url": EDUCATIONAL_LINK,
            "last_updated": "N/A",
            "refused": False,
        }

    chunk_text = (retrieved[0].get("text") or "").strip()
    # When LLM (e.g. Groq) is provided, use it to answer from context; fall back to scraped chunk text.
    if llm_call:
        context = format_context(retrieved)
        user_prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer in at most 3 sentences, using only the context. No investment advice."
        answer = (llm_call(system=SYSTEM_PROMPT, user=user_prompt) or "").strip()
        if not answer or len(answer) < 10:
            answer = chunk_text
    else:
        answer = chunk_text
    if not answer:
        answer = "This information was not found in our sources."
    # For long text, keep at most 3 sentences (split on ". " so decimals like 0.23% stay intact)
    if len(answer) > 300:
        sentences = answer.replace("..", ".").split(". ")
        sentences = [s.strip().rstrip(".") for s in sentences if s.strip()][:3]
        answer = ". ".join(sentences)
    if answer and not answer.endswith("."):
        answer += "."

    # If user asked about a specific scheme but we only have a generic chunk, add scheme link
    top_is_generic = retrieved and not retrieved[0].get("scheme_id")
    if scheme_info and scheme_info.get("url") and top_is_generic:
        name = scheme_info.get("scheme_name") or "this scheme"
        answer = answer.rstrip(". ") + f". For scheme-specific details on {name}, see the link below."
        citation_url = scheme_info["url"]
        last_updated = last_updated or "N/A"

    # Ensure every answer has a proper citation link (chunks should have source_url; fallback to educational)
    if not (citation_url or "").strip():
        citation_url = EDUCATIONAL_LINK

    # Never return empty answer when we have retrieved data — always show scraped content or fallback
    answer = (answer or "").strip()
    if not answer and chunk_text:
        answer = chunk_text
    if not answer:
        answer = "This information was not found in our sources."

    return {
        "answer": answer,
        "citation_url": (citation_url or "").strip(),
        "last_updated": last_updated or "N/A",
        "refused": False,
    }
