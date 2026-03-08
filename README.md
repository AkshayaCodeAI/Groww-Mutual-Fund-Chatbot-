# Groww Mutual Fund FAQ Chatbot (RAG)

Facts-only RAG chatbot for Groww mutual fund scheme FAQs. No investment advice; one citation per answer.

---

## Ready to run (3 steps)

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Build RAG chunks** (uses phase1 glossary + howto; no scrape needed)
```bash
python -m phase2.chunk
```

**3. Start the app**
```bash
streamlit run phase5/streamlit_app.py
```

Then open **http://localhost:8501** in your browser. You can ask e.g. “What is Riskometer?”, “Expense ratio?”, “How to update KYC?”.

---

## One-command run (Unix/macOS)

```bash
chmod +x run.sh && ./run.sh
```

On Windows: `run.bat`

---

## Deploy to Streamlit Community Cloud

1. Push this repo to **GitHub**.
2. Go to **[share.streamlit.io](https://share.streamlit.io)** → **New app**.
3. Set **Main file path** to `phase5/streamlit_app.py`.
4. (Optional) In **Settings → Secrets**, add `GROQ_API_KEY` (or `XAI_API_KEY`) and/or `CHAT_API_URL`.
5. Click **Deploy**.

See **phase6/DEPLOYMENT.md** for full steps and Docker.

---

## Optional: run with Backend API

**Terminal 1 – Backend**
```bash
uvicorn phase4.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 – Frontend**
```bash
streamlit run phase5/streamlit_app.py
```

Phase 5 uses the API if `CHAT_API_URL` (default `http://localhost:8000`) is reachable; otherwise it runs the RAG pipeline in-process.

---

## Optional: full data (scrape scheme pages)

To include scheme-specific data (expense ratio, exit load, etc. per fund):

```bash
python -m phase2.scrape   # needs network
python -m phase2.parse
python -m phase2.chunk
```

Then run the app as above.

---

## Project layout

| Folder    | Description |
|-----------|-------------|
| **phase1/** | Data & schema (sources.json, glossary, howto) |
| **phase2/** | Ingestion (scrape, parse, chunk, embed) |
| **phase3/** | RAG pipeline (retrieve, generate) |
| **phase4/** | Backend API (FastAPI) |
| **phase5/** | Frontend (Streamlit) |
| **phase6/** | Deployment notes |
| **data/**   | Generated chunks (and raw/parsed if you scrape) |
| **docs/**   | ARCHITECTURE.md |<img width="902" height="814" alt="Screenshot 2026-03-08 at 7 18 55 PM" src="https://github.com/user-attachments/assets/f46f0998-878b-4336-8d53-41dc915088b1" />


---

## Config

- **.env** – Optional. Copy `.env.example` to `.env` and set `CHAT_API_URL` if the API runs elsewhere.
- **requirements.txt** – Python dependencies for all phases.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [phase6/DEPLOYMENT.md](phase6/DEPLOYMENT.md) for details.

<img width="902" height="814" alt="Screenshot 2026-03-08 at 7 18 55 PM" src="https://github.com/user-attachments/assets/fc363cc9-e297-429b-bbdf-17c979fe6cf9" />

Question Asked 

What is the investment objective of HDFC Silver ETF FoF Direct Growth?

What are the latest NAV and 3-year returns of this fund?

What level of risk is associated with this silver-based fund?

What is the minimum SIP or lump-sum investment required?

What assets does this fund primarily invest in?

Who is the fund manager and what is the expense ratio of this scheme?






