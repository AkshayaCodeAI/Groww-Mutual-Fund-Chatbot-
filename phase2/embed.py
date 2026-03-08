"""
Phase 2.4 (Optional): Embed — Generate embeddings and build vector index.
Reads data/chunks/all_chunks.jsonl; writes to data/embeddings/.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # project root
DATA_DIR = ROOT / "data"
CHUNKS_PATH = DATA_DIR / "chunks" / "all_chunks.jsonl"
EMBED_DIR = DATA_DIR / "embeddings"


def load_chunks() -> list[dict]:
    chunks = []
    if not CHUNKS_PATH.exists():
        return chunks
    with open(CHUNKS_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))
    return chunks


def embed_with_sentence_transformers(chunks: list[dict], model_name: str = "all-MiniLM-L6-v2") -> list[list[float]]:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(model_name)
    texts = [c.get("text", "") for c in chunks]
    return model.encode(texts).tolist()


def build_faiss_index(vectors: list[list[float]], save_path: Path) -> None:
    import numpy as np
    try:
        import faiss
    except ImportError:
        raise ImportError("pip install faiss-cpu")
    x = np.array(vectors, dtype="float32")
    index = faiss.IndexFlatL2(x.shape[1])
    index.add(x)
    faiss.write_index(index, str(save_path))


def run_embed() -> None:
    EMBED_DIR.mkdir(parents=True, exist_ok=True)
    chunks = load_chunks()
    if not chunks:
        print("No chunks found. Run chunk.py first.")
        return
    try:
        vectors = embed_with_sentence_transformers(chunks)
    except ImportError:
        print("Optional: pip install sentence-transformers")
        return
    meta_path = EMBED_DIR / "chunk_meta.json"
    meta = [
        {"text": c.get("text", "")[:500], "source_url": c.get("source_url", ""), "last_updated": c.get("last_updated", ""), "scheme_name": c.get("scheme_name"), "field": c.get("field", "")}
        for c in chunks
    ]
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=0, ensure_ascii=False)
    try:
        index_path = EMBED_DIR / "index.faiss"
        build_faiss_index(vectors, index_path)
        print(f"Saved FAISS index -> {index_path}, meta -> {meta_path}")
    except ImportError:
        with open(EMBED_DIR / "vectors.json", "w") as f:
            json.dump(vectors, f)
        print("Saved vectors. Install faiss-cpu for index.")
    print("Done.")


if __name__ == "__main__":
    run_embed()
