import json
import os
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

BASE_DIR = Path(__file__).resolve().parent
INDEX_PATH = BASE_DIR / "faiss_index.bin"
TEXTS_PATH = BASE_DIR / "stored_texts.json"
MODEL_NAME = "all-mpnet-base-v2"

model = None
index = None
stored_texts = None


def _load_assets():
    global model, index, stored_texts

    if model is None:
        model = SentenceTransformer(MODEL_NAME)

    if index is None:
        if not INDEX_PATH.exists():
            raise FileNotFoundError("faiss_index.bin not found. Run build_index.py first.")
        index = faiss.read_index(str(INDEX_PATH))

    if stored_texts is None:
        if not TEXTS_PATH.exists():
            raise FileNotFoundError("stored_texts.json not found. Run build_index.py first.")
        with TEXTS_PATH.open("r", encoding="utf-8") as f:
            stored_texts = json.load(f)


def retrieve_many(queries, k=1):
    """Retrieve context for multiple queries in one embedding-model pass."""
    if not queries:
        return []

    _load_assets()
    embeddings = model.encode(queries)
    _, indices = index.search(np.asarray(embeddings, dtype=np.float32), k)
    return [
        [stored_texts[i] for i in row if 0 <= i < len(stored_texts)]
        for row in indices
    ]


def retrieve(query, k=1):
    return retrieve_many([query], k)[0]
