# Phase 1: Data Schema — Mutual Fund FAQ RAG

Schema for data extracted from Groww scheme pages and used for chunking, retrieval, and citation.

---

## Scheme-level fields (per scheme page)

| # | Field | Type | Description |
|---|-------|------|-------------|
| 1 | type | string | Direct or Regular |
| 2 | expense_ratio | string | TER % (e.g. "0.23%") |
| 3 | exit_load | string | Exit load text (e.g. "1% if redeemed within 15 days") |
| 4 | min_sip | string | Minimum SIP in ₹ |
| 5 | min_lumpsum | string | Minimum lump sum in ₹ |
| 6 | lock_in_period | string | Lock-in if any (e.g. "3 years" for ELSS) or null |
| 7 | benchmark | string | Benchmark name |
| 8 | risk | string | Riskometer / risk level (e.g. "Very High") |
| 9 | fund_manager | string or array | Fund manager name(s) |
| 10 | launch_date | string | Scheme launch date |
| 11 | category | string | Category (e.g. "Commodities Silver") |
| 12 | scheme_type | string | Scheme type (e.g. FoF, Open-ended) |
| 13 | asset_allocation | string or object | Asset allocation summary |
| 14 | top_holdings | array | Top holdings (name, sector, instruments, assets %) |
| 15 | return_1y | string | 1-year return (display only; no advice) |
| 16 | return_3y | string | 3-year return |
| 17 | return_5y | string | 5-year return (if available) |
| 18 | elss_tax_benefit | string | ELSS tax benefit (if applicable) |
| 19 | ltcg_tax_rule | string | Long-term capital gains tax rule |
| 20 | stcg_tax_rule | string | Short-term capital gains tax rule |
| 21 | tax_implication | string | Combined tax implication text |
| 22 | stamp_duty | string | Stamp duty % and effective date |
| 23 | fund_house | string | AMC / Fund house name |
| 24 | fund_house_url | string | AMC page URL on Groww (if available) |
| 25 | about_scheme | string | About scheme + investment objective |
| 26 | investment_objective | string | From SID / scheme section |
| 27 | min_1st_investment | string | Minimum for first investment |
| 28 | min_2nd_investment | string | Minimum for subsequent investment |
| 29 | one_time_sip | string | One-time SIP info (if on page) |
| 30 | holding_analysis | string | Holding analysis section |
| 31 | advanced_ratios | string | Advanced ratios (e.g. Sharpe) if on page |
| 32 | annualised_returns_definition | string | Glossary: annualised returns |
| 33 | absolute_returns_definition | string | Glossary: absolute returns |
| 34 | expense_ratio_definition | string | Glossary: expense ratio |
| 35 | exit_load_definition | string | Glossary: exit load |
| 36 | stamp_duty_definition | string | Glossary: stamp duty |
| 37 | tax_definition | string | Glossary: tax (LTCG/STCG) |
| 38 | faqs | array | FAQ items: { "question", "answer" } |

## Metadata (every scheme document)

| Field | Type | Description |
|-------|------|-------------|
| scheme_id | string | Slug from URL (e.g. `hdfc-silver-etf-fof-direct-growth`) |
| scheme_name | string | Display name |
| source_url | string | Canonical Groww scheme page URL |
| last_updated | string (YYYY-MM-DD) | Date of ingestion |

---

## How-to / procedural (from Help or static)

Used for "How to download statement", "How to download capital gains report", "How to update KYC".

| Field | Type | Description |
|-------|------|-------------|
| content_type | string | "howto" |
| topic | string | e.g. download_statement, download_capital_gains, update_kyc |
| title | string | Short title |
| body | string | Steps or description |
| source_url | string | e.g. Groww Help URL |
| last_updated | string | YYYY-MM-DD |

---

## Glossary (static chunks)

Used for NAV meaning, Riskometer meaning, and other "Understand terms" definitions.

| Field | Type | Description |
|-------|------|-------------|
| content_type | string | "glossary" |
| topic | string | e.g. nav_meaning, riskometer_meaning |
| title | string | Short title |
| text | string | Definition body |
| source_url | string | Citation URL |
| last_updated | string | YYYY-MM-DD |

---

## Chunk metadata (for vector store)

Each chunk stored for RAG must include:

- **text** — Chunk content.
- **scheme_id** — If scheme-specific; else null.
- **scheme_name** — If scheme-specific; else null.
- **source_url** — URL to cite in the answer.
- **field** or **section** — e.g. "expense_ratio", "exit_load", "faq", "about_scheme", "glossary".
- **last_updated** — For "Last updated from sources".
