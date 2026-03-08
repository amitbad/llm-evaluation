import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
CHUNKS_FILE = os.path.join(SCRIPT_DIR, "chunks.json")

_model  = None
_chunks = None
_embeddings = None


def _load():
    global _model, _chunks, _embeddings

    if _chunks is not None:
        return

    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        _chunks = json.load(f)

    _model = SentenceTransformer("all-MiniLM-L6-v2")

    texts = [c["text"] for c in _chunks]
    _embeddings = _model.encode(texts, convert_to_numpy=True)


def retrieve(query, top_k=3):
    _load()

    query_vec = _model.encode([query], convert_to_numpy=True)

    # Cosine similarity
    norms = np.linalg.norm(_embeddings, axis=1, keepdims=True)
    normed = _embeddings / np.clip(norms, 1e-10, None)
    query_normed = query_vec / np.clip(np.linalg.norm(query_vec), 1e-10, None)

    scores = (normed @ query_normed.T).flatten()
    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for i in top_indices:
        results.append({
            "id":     _chunks[i]["id"],
            "source": _chunks[i]["source"],
            "text":   _chunks[i]["text"],
            "score":  round(float(scores[i]), 4)
        })

    return results


if __name__ == "__main__":
    test_queries = [
        "How long does it take to open a NextGen account?",
        "What is the penalty for an unarranged overdraft?",
        "Which professional certification providers are approved for LearnFund?",
    ]

    for q in test_queries:
        print(f"\nQuery: {q}")
        chunks = retrieve(q, top_k=3)
        for c in chunks:
            print(f"  [{c['score']}] (chunk {c['id']}) {c['source']}")
            print(f"    {c['text'][:100]}...")
