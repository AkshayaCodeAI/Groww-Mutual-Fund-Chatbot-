#!/usr/bin/env bash
# Ready run: install deps, build chunks (glossary + howto), start Streamlit.
# From project root: ./run.sh   or   bash run.sh

set -e
cd "$(dirname "$0")"

echo "=== Installing dependencies ==="
python3 -m pip install -q -r requirements.txt

echo "=== Building RAG chunks (glossary + howto) ==="
python3 -m phase2.chunk

echo "=== Starting Streamlit app ==="
echo "Open http://localhost:8501 in your browser."
echo "Press Ctrl+C to stop."
exec python3 -m streamlit run phase5/streamlit_app.py --server.port 8501 --server.headless true
