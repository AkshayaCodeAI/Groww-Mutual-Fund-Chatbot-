# Data (generated)

Generated outputs from **Phase 2** (ingestion). Phase 1 config and schema live in **phase1/**.

| Path | Produced by |
|------|-------------|
| `raw_pages/*.html` | phase2/scrape.py |
| `parsed/*.json` | phase2/parse.py |
| `chunks/all_chunks.jsonl` | phase2/chunk.py |
| `embeddings/` | phase2/embed.py (optional) |

Run from project root: `python -m phase2.scrape`, `python -m phase2.parse`, `python -m phase2.chunk`, `python -m phase2.embed`.
