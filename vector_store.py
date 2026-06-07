#vector_store.py

import faiss
import pickle
import numpy as np

INDEX_FILE = "faiss_index.bin"
CHUNKS_FILE = "chunks.pkl"

def store_vectors(embeddings, chunks):
    if embeddings is None or len(chunks) == 0:
        return

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)

    index.add(np.array(embeddings))

    faiss.write_index(index, INDEX_FILE)

    # ✅ Store ONLY the chunks used for embeddings
    with open(CHUNKS_FILE, "wb") as f:
        pickle.dump(chunks, f)


def load_vector_store():
    index = faiss.read_index(INDEX_FILE)

    with open(CHUNKS_FILE, "rb") as f:
        chunks = pickle.load(f)

    return index, chunks


def reset_vector_store():
    import os
    if os.path.exists(INDEX_FILE):
        os.remove(INDEX_FILE)
    if os.path.exists(CHUNKS_FILE):
        os.remove(CHUNKS_FILE)