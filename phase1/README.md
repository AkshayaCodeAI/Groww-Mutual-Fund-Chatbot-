# Phase 1: Data & Schema

Phase 1 deliverables (config and schema):

| File | Description |
|------|-------------|
| `sources.json` | Scheme page URLs (4 schemes) + Groww Help URL + educational links |
| `schema.md` | Field list and metadata for extraction and RAG chunks |
| `glossary_chunks.json` | Static glossary (NAV meaning, Riskometer meaning, annualised/absolute returns, expense ratio, exit load, stamp duty, tax) |
| `howto_chunks.json` | How-to: download statement, download capital gains report, update KYC (source: Groww Help) |

Phase 2 reads from this folder and writes to `data/` at project root.
