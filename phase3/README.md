# Phase 3: RAG Pipeline

Retrieve + generate with constraints (no advice, one citation, ≤3 sentences).

**Deliverables:**

| File | Description |
|------|-------------|
| `config/prompts.py` | System prompt, refusal message, educational link, refusal triggers |
| `retrieve.py` | Load chunks from `data/chunks/all_chunks.jsonl`; keyword retrieval; optional scheme filter; returns top-k with source_url, last_updated |
| `generate.py` | Refusal for advice/return-comparison queries; format context; produce answer (fallback: first chunk; optional LLM) |
| `pipeline.py` | Single entry: `run_pipeline(query, top_k=5, scheme_id=None, llm_call=None)` → `{ answer, citation_url, last_updated, refused }` |

**Run from project root:**

```bash
python -m phase3.pipeline "What is Riskometer?"
```

Or in code: `from phase3.pipeline import run_pipeline`
