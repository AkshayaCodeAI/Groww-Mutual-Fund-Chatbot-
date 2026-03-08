# Phase 6: Deployment (Streamlit)

Deploy Backend (Phase 4) and Frontend (Phase 5). See **DEPLOYMENT.md** in this folder for run instructions, Streamlit Cloud, and Docker.

**Quick run from project root:**

```bash
# Terminal 1: Backend (when Phase 4 is implemented)
uvicorn phase4.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
streamlit run phase5/streamlit_app.py
```
