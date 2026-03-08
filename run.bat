@echo off
REM Ready run: install deps, build chunks, start Streamlit.
REM From project root: run.bat

cd /d "%~dp0"

echo === Installing dependencies ===
python -m pip install -q -r requirements.txt

echo === Building RAG chunks (glossary + howto) ===
python -m phase2.chunk

echo === Starting Streamlit app ===
echo Open http://localhost:8501 in your browser.
echo Press Ctrl+C to stop.
streamlit run phase5/streamlit_app.py --server.port 8501 --server.headless true
