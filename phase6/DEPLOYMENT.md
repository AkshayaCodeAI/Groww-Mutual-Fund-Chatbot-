# Deployment (Phase 6) — Streamlit

Deploy the **FundWise** Groww MF FAQ Chatbot with **Streamlit** (e.g. Streamlit Community Cloud).

---

## Deploy to Streamlit Community Cloud

### 1. Push repo to GitHub

Ensure your project is in a GitHub repository (with `data/chunks/all_chunks.jsonl` committed, or the app will build chunks on first run from phase1 + parsed data if present).

### 2. Connect on Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub.
2. Click **“New app”**.
3. **Repository:** `your-username/Groww-Mutual-Fund-Chatbot-` (or your repo name).  
4. **Branch:** `main` (or your default branch).  
5. **Main file path:** `phase5/streamlit_app.py`  
6. **App URL:** choose a subdomain (e.g. `groww-mf-faq`).

### 3. Set secrets (optional)

In the app’s **Settings → Secrets**, add:

```toml
# Optional: Backend API URL (if you deploy Phase 4 separately)
CHAT_API_URL = "https://your-api.example.com"

# Optional: xAI Grok API key for LLM-based answers
XAI_API_KEY = "gsk_your_key_here"
```

- If you don’t set `CHAT_API_URL`, the app uses **in-process RAG** (Phase 3).  
- If you don’t set `XAI_API_KEY`, answers use the first retrieved chunk (no LLM call).

### 4. Deploy

Click **“Deploy”**. Streamlit will install from `requirements.txt` and run:

```bash
streamlit run phase5/streamlit_app.py
```

Config is read from **`.streamlit/config.toml`** (port 8501, headless, etc.).

---

## What gets run

| Item | Purpose |
|------|--------|
| **Main file** | `phase5/streamlit_app.py` |
| **requirements.txt** | streamlit, httpx, beautifulsoup4, fastapi, uvicorn, pydantic |
| **.streamlit/config.toml** | Server port 8501, headless, CORS/XSRF |
| **Data** | `data/chunks/all_chunks.jsonl` (committed) or built on first run from phase1 + `data/parsed/` if present |

---

## Run locally (same as deploy)

From **project root**:

```bash
pip install -r requirements.txt
streamlit run phase5/streamlit_app.py
```

Or use the script:

```bash
./run.sh
```

- **With API:** set `CHAT_API_URL` or start Phase 4 (e.g. `uvicorn phase4.main:app --port 8000`) and point the app to it.  
- **Without API:** app uses Phase 3 RAG in-process (default).

---

## Environment variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CHAT_API_URL` | Phase 4 API base URL | `http://localhost:8000` |
| `XAI_API_KEY` | xAI Grok API key for LLM answers | not set (chunk-only answers) |

---

## Docker (optional)

From project root:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "phase5/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0"]
```

```bash
docker build -t fundwise .
docker run -p 8501:8501 -e XAI_API_KEY=your_key fundwise
```

---

## Checklist before deploy

- [ ] Repo is on GitHub.
- [ ] `requirements.txt` and `.streamlit/config.toml` are in the repo.
- [ ] Either `data/chunks/all_chunks.jsonl` is committed, or `data/parsed/*.json` + phase1 glossary/howto exist so the app can build chunks on first run.
- [ ] Secrets (e.g. `XAI_API_KEY`, `CHAT_API_URL`) set in Streamlit Cloud if you use them.
