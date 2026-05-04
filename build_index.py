import json
import os
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_PATH = BASE_DIR / "data" / "medical_knowledge.json"
INDEX_PATH = BASE_DIR / "faiss_index.bin"
TEXTS_PATH = BASE_DIR / "stored_texts.json"


with KNOWLEDGE_PATH.open("r", encoding="utf-8") as f:
    knowledge = json.load(f)

texts = []
for item in knowledge:
    text = f"""
    Test: {item['test_name']}
    Category: {item['category']}
    Low Meaning: {item['low_meaning']}
    High Meaning: {item['high_meaning']}
    """
    texts.append(text)

model = SentenceTransformer("all-mpnet-base-v2")
embeddings = model.encode(texts)

dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

faiss.write_index(index, str(INDEX_PATH))

with TEXTS_PATH.open("w", encoding="utf-8") as f:
    json.dump(texts, f)

print("FAISS index built successfully.")
