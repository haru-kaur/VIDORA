# embeddings.py
from sentence_transformers import SentenceTransformer
import numpy as np
import re

model = SentenceTransformer('all-MiniLM-L6-v2')

def clean_text(text):
    # remove weird unicode and non-text characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def create_embeddings(chunks):
    clean_chunks = []

    for chunk in chunks:
        if not isinstance(chunk, str):
            continue

        chunk = clean_text(chunk)

        # skip garbage chunks
        if len(chunk) < 50:
            continue

        # very important: limit size (tokenizer crash fix)
        chunk = chunk[:800]

        clean_chunks.append(chunk)

    embeddings = model.encode(clean_chunks, convert_to_numpy=True)
    return embeddings, clean_chunks