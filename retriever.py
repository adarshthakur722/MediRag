import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

model = SentenceTransformer("all-mpnet-base-v2")
index = faiss.read_index("faiss_index.bin")

with open("stored_texts.json", "r") as f:
    stored_texts = json.load(f)

def retrieve(query, k=1):
    embedding = model.encode([query])
    distances, indices = index.search(np.array(embedding), k)
    return [stored_texts[i] for i in indices[0]]