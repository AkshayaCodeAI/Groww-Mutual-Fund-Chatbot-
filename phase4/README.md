# Phase 4: Backend

HTTP API for the chatbot (consumed by Phase 5 Frontend).

**Deliverables:**

| Item | Description |
|------|-------------|
| `main.py` | FastAPI app: `POST /chat`, `GET /schemes`; orchestrates Phase 3 RAG; CORS enabled |
| Run | From project root: `uvicorn phase4.main:app --host 0.0.0.0 --port 8000` |

**Endpoints:**

- **POST /chat** — Body: `{ "query": "..." }`. Response: `{ "answer", "citation_url", "last_updated", "refused" }`.
- **GET /schemes** — Response: `{ "schemes": [ { "scheme_id", "scheme_name", "url" }, ... ] }`.

Config: default port 8000; override with `--port`. Frontend uses `CHAT_API_URL` (default `http://localhost:8000`).
