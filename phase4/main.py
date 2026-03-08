"""
Phase 4: Backend — FastAPI API for the Groww MF FAQ Chatbot.
Orchestrates Phase 3 RAG pipeline. Consumed by Phase 5 Frontend.

Run from project root: uvicorn phase4.main:app --host 0.0.0.0 --port 8000
"""

import json
import sys
from pathlib import Path

# Project root so phase3 is importable
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from phase3.pipeline import run_pipeline

app = FastAPI(
    title="Groww MF FAQ Chatbot API",
    description="Facts-only FAQ for mutual fund schemes. No investment advice.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SOURCES_PATH = PROJECT_ROOT / "phase1" / "sources.json"


class ChatRequest(BaseModel):
    query: str
    scheme_id: str | None = None  # optional: for pronoun resolution ("this fund" -> last scheme)


class ChatResponse(BaseModel):
    answer: str
    citation_url: str
    last_updated: str
    refused: bool = False


@app.get("/schemes")
def get_schemes():
    """Return list of supported schemes and URLs (for Frontend/UI)."""
    if not SOURCES_PATH.exists():
        return {"schemes": []}
    with open(SOURCES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return {"schemes": data.get("scheme_pages", [])}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Answer a factual question using Phase 3 RAG. One citation, last_updated. Refuses advice/opinion questions. scheme_id resolves pronouns like 'this fund'."""
    result = run_pipeline(req.query, scheme_id=req.scheme_id)
    return ChatResponse(
        answer=result["answer"],
        citation_url=result.get("citation_url", ""),
        last_updated=result.get("last_updated", ""),
        refused=result.get("refused", False),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
