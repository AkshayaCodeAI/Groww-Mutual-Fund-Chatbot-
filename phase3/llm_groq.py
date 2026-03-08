"""
Optional LLM caller for Phase 3 using Groq API (Llama etc.).
When GROQ_API_KEY is set, the pipeline can use this for answer generation from context.
"""

import json
import os
import urllib.request

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"  # or llama-3.1-8b-instant for faster responses


def groq_chat(system: str, user: str, api_key: str | None = None) -> str:
    """
    Call Groq chat completions. Returns the assistant message content.
    api_key defaults to os.environ.get("GROQ_API_KEY").
    """
    key = api_key or os.environ.get("GROQ_API_KEY")
    if not key:
        return ""
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    data = json.dumps({
        "model": GROQ_MODEL,
        "messages": messages,
        "max_tokens": 256,
        "temperature": 0.2,
    }).encode("utf-8")
    req = urllib.request.Request(
        GROQ_API_URL,
        data=data,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            out = json.loads(resp.read().decode())
    except Exception:
        return ""
    choice = (out.get("choices") or [None])[0]
    if not choice:
        return ""
    msg = choice.get("message") or {}
    return (msg.get("content") or "").strip()


def make_llm_call(api_key: str | None = None):
    """Return a function(system=..., user=...) -> answer string for use in generate_answer."""
    def _call(system: str, user: str) -> str:
        return groq_chat(system, user, api_key=api_key)
    return _call
