import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Load medical knowledge
with open("data/medical_knowledge.json", "r") as f:
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

# Load embedding model
model = SentenceTransformer("all-mpnet-base-v2")
embeddings = model.encode(texts)

dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

faiss.write_index(index, "faiss_index.bin")

with open("stored_texts.json", "w") as f:
    json.dump(texts, f)

print("✅ FAISS index built successfully.")