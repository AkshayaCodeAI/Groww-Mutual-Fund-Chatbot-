# RAG-Based Mutual Fund FAQ Chatbot (Groww) — Phased Architecture

## Overview

A **facts-only** RAG chatbot for Groww mutual fund scheme FAQs. Delivered in **six phases**: Data & Schema, Ingestion, RAG Pipeline, **Backend**, **Frontend**, and **Deployment (Streamlit)**.

---

## Phase 1: Data & Schema

**Goal:** Define sources, schema, and raw data capture.

| Step | Deliverable |
|------|-------------|
| 1.1 | **Data sources** — List of 4 scheme URLs + optional Groww Help URL |
| 1.2 | **Schema** — Field list (Type, Expense ratio, Exit load, Min SIP, Min lump sum, Lock-in, Benchmark, Risk, Fund Manager, Launch date, Category, Scheme type, Asset allocation, Top holdings, Returns, Tax rules, How-to, Glossary, FAQs, Fund house, About scheme, Min investments, Stamp duty, etc.) |
| 1.3 | **Source config** — `data/sources.json` with scheme_id, scheme_name, url |
| 1.4 | **Glossary** — Static chunks for NAV meaning, Riskometer meaning (e.g. `data/glossary_chunks.json`) |

**Outputs:** `phase1/sources.json`, `phase1/schema.md`, `phase1/glossary_chunks.json`

---

## Phase 2: Ingestion Pipeline

**Goal:** Fetch, parse, chunk, and optionally embed.

| Step | Deliverable |
|------|-------------|
| 2.1 | **Scrape** — Fetch HTML from scheme pages (respect robots.txt, rate limits); read `phase1/sources.json`; save to `data/raw_pages/*.html` |
| 2.2 | **Parse** — Extract structured fields per schema; save to `data/parsed/*.json` |
| 2.3 | **Chunk** — Build RAG chunks (text + metadata: scheme_id, source_url, field, last_updated); merge `phase1/glossary_chunks.json`; write `data/chunks/all_chunks.jsonl` |
| 2.4 | **Embed (optional)** — Generate embeddings; build vector index (e.g. FAISS/Chroma); save to `data/embeddings/` |

**Outputs:** `phase2/scrape.py`, `phase2/parse.py`, `phase2/chunk.py`, `phase2/embed.py`

---

## Phase 3: RAG Pipeline

**Goal:** Retrieve + generate with constraints (no advice, one citation, ≤3 sentences).

| Step | Deliverable |
|------|-------------|
| 3.1 | **Retrieve** — Load chunks; vector or keyword search; optional scheme filter; return top-k with source_url, last_updated |
| 3.2 | **Generate** — System prompt (facts-only, no advice, no return computation); refusal for “should I buy/sell” and return comparisons; fallback or LLM answer |
| 3.3 | **Pipeline** — Single entry: query → retrieve → generate → { answer, citation_url, last_updated } |

**Outputs:** `phase3/retrieve.py`, `phase3/generate.py`, `phase3/pipeline.py`, `phase3/config/prompts.py`

---

## Phase 4: Backend

**Goal:** Server-side API and business logic for the chatbot (consumed by Frontend).

| Step | Deliverable |
|------|-------------|
| 4.1 | **API** — HTTP endpoints: **POST /chat** (request: `{ "query": "..." }`; response: `{ "answer", "citation_url", "last_updated", "refused" }`), **GET /schemes** (list of supported schemes and URLs) |
| 4.2 | **Orchestration** — API invokes Phase 3 RAG pipeline (retrieve → generate); no UI logic in backend |
| 4.3 | **CORS** — Enabled for frontend origin(s) or allowed origins |
| 4.4 | **Config** — API base URL / port (e.g. `http://localhost:8000`) configurable via env |

**Outputs:** `phase4/main.py` (FastAPI), `requirements.txt` (api deps)

---

## Phase 5: Frontend

**Goal:** User-facing UI that calls the Backend and displays answers with one citation and last-updated line.

| Step | Deliverable |
|------|-------------|
| 5.1 | **Streamlit app** — Single entry (e.g. `phase5/streamlit_app.py`) with: welcome line, 3 example questions, disclaimer “Facts-only. No investment advice.”, chat input |
| 5.2 | **Display** — Show answer (≤3 sentences), one citation link, and “Last updated from sources: &lt;date&gt;”; show refusal message + educational link for advice/opinion questions |
| 5.3 | **Backend integration** — Frontend calls Phase 4 API (e.g. `CHAT_API_URL`); optional fallback to Phase 3 RAG in-process when API is not available |
| 5.4 | **Run** — `streamlit run phase5/streamlit_app.py` (from project root) with optional `--server.port`; env `CHAT_API_URL` for API base URL |

**Outputs:** `phase5/streamlit_app.py` (Streamlit UI)

---

## Phase 6: Deployment (Streamlit)

**Goal:** Deploy Backend and Frontend; production run is via Streamlit.

| Step | Deliverable |
|------|-------------|
| 6.1 | **Backend** — Run API (e.g. `uvicorn phase4.main:app`) on a host/port; or run RAG in-process inside Streamlit for single-process deploy |
| 6.2 | **Frontend** — Run Streamlit app (`streamlit run phase5/streamlit_app.py`); Streamlit Cloud, Docker, or self-hosted |
| 6.3 | **Config** — Document port, env vars (`CHAT_API_URL`), and optional reverse proxy (e.g. Nginx) |
| 6.4 | **Docs** — Deployment steps in [phase6/DEPLOYMENT.md](phase6/DEPLOYMENT.md) (Streamlit Cloud, Docker, self-hosted) |

**Outputs:** Run instructions, `phase6/DEPLOYMENT.md`

---

## Phase Summary

| Phase | Name | Main deliverable |
|-------|------|------------------|
| 1 | Data & Schema | phase1/: sources.json, schema.md, glossary_chunks.json |
| 2 | Ingestion | phase2/: scrape → parse → chunk → (embed); writes data/ |
| 3 | RAG Pipeline | phase3/: retrieve → generate → answer + citation |
| 4 | **Backend** | phase4/: FastAPI /chat, /schemes; RAG orchestration |
| 5 | **Frontend** | phase5/: Streamlit UI; answer + citation + last updated |
| 6 | **Deployment (Streamlit)** | phase6/: Run instructions, DEPLOYMENT.md |

**Phases at a glance:**

```
Phase 1: phase1/
    → sources.json, schema.md, glossary_chunks.json

Phase 2: phase2/
    → scrape.py → parse.py → chunk.py → (embed.py)
    → reads phase1/; writes data/raw_pages/, data/parsed/, data/chunks/, data/embeddings/

Phase 3: phase3/
    → retrieve.py + generate.py + pipeline.py
    → query → answer + citation_url + last_updated

Phase 4: phase4/
    → FastAPI: POST /chat, GET /schemes
    → Orchestrates RAG; CORS, config

Phase 5: phase5/
    → streamlit_app.py: welcome, examples, disclaimer, chat
    → Calls phase4 (CHAT_API_URL) or phase3 in-process; shows answer + citation + last updated

Phase 6: phase6/
    → DEPLOYMENT.md, run Backend + Frontend
    → Streamlit Cloud / Docker / self-hosted
```

---

## Data Sources (Reference)

| URL | Scheme |
|-----|--------|
| https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth | HDFC Silver ETF FoF Direct Growth |
| https://groww.in/mutual-funds/sbi-gold-fund-direct-growth | SBI Gold Fund Direct Growth |
| https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth | HDFC Mid Cap Fund Direct Growth |
| https://groww.in/mutual-funds/bandhan-small-cap-fund-direct-growth | Bandhan Small Cap Fund Direct Growth |

---

## Key Constraints (All Phases)

- **No performance claims** — Do not compute/compare returns; link to factsheet if asked.
- **No investment advice** — Refuse “should I buy/sell” with polite message + educational link.
- **Clarity** — Answers ≤3 sentences; “Last updated from sources: &lt;date&gt;” on every answer.
- **One citation** — Single citation_url per response.
- **Deployment** — Backend (API) + Frontend (Streamlit); deployed as a **Streamlit** app (Phase 6).
