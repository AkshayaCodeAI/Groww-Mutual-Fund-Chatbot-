# Phase 2: Ingestion

Scrapes the **shared scheme URLs** from phase1 and extracts all important data. Reads **phase1/** (sources.json, glossary_chunks.json, howto_chunks.json). Writes to **data/** at project root.

**Data scraped/parsed (36 fields):**  
1. Type (Direct/Regular) 2. Expense ratio 3. Exit load 4. Minimum SIP 5. Minimum lump sum 6. Lock-in period 7. Benchmark 8. Risk 9. Fund Manager 10. Launch date 11. Category 12. Scheme type 13. Asset allocation 14. Top holdings 15–17. 1Y/3Y/5Y returns 18. ELSS tax benefit 19. LTCG tax rule 20. STCG tax rule 21. How to download statement 22. How to download capital gains report 23. How to update KYC 24. NAV meaning 25. Riskometer meaning 26. All FAQs (Q&A) 27. Fund House 28. About Scheme 29. One Time SIP 30. Holding Analysis 31. Advanced Ratios 32. Minimum investments 33. Annualised returns 34. Absolute returns 35. Stamp duty 36. Tax implication  

(21–23, 24–25 from phase1 static chunks; rest from scheme page HTML.)

Run from project root:

1. **Scrape:** `python -m phase2.scrape` → `data/raw_pages/*.html`
2. **Parse:** `python -m phase2.parse` → `data/parsed/*.json`
3. **Chunk:** `python -m phase2.chunk` → `data/chunks/all_chunks.jsonl` (includes glossary + howto; every chunk has a `source_url` for proper citation links)
4. **Embed (optional):** `python -m phase2.embed` → `data/embeddings/`
5. **Validate (optional):** `python -m phase2.validate_data` → checks every chunk has a valid Groww `source_url` and sample questions get answers with proper citation links
