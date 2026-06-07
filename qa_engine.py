# qa_engine.py
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
from sentence_transformers import CrossEncoder


reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

load_dotenv()

from groq import Groq

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

print("Loaded GROQ KEY:", os.getenv("GROQ_API_KEY"))

model = SentenceTransformer('all-MiniLM-L6-v2')

def load_vector_store():
    index = faiss.read_index("faiss_index.bin")
    with open("chunks.pkl", "rb") as f:
        chunks = pickle.load(f)
    return index, chunks

def load_full_document():
    try:
        with open("full_document.txt", "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except:
        return ""

def retrieve_answer(question, top_k=8):
    index, chunks = load_vector_store()
    full_doc = load_full_document()
    q = question.lower()

    # ----------- ✅ DOCUMENT SCAN FIRST (for factual queries) -------------
    factual_keywords = [
        "submitted by", "name", "author", "roll no",
        "figure", "table", "title", "course", "university"
    ]

    if any(word in q for word in factual_keywords):
        return [full_doc[:4000]]

    # ----------- 🔍 VECTOR SEARCH (semantic questions) --------------------
    question_embedding = model.encode([question])
    question_embedding = np.array(question_embedding)

    distances, indices = index.search(question_embedding, top_k)

    # ✅ CRITICAL FIX — keep only valid indices
    safe_chunks = []
    for i in indices[0]:
        if 0 <= i < len(chunks):
            safe_chunks.append(chunks[i])

    # If very small data (image/video) and FAISS returns junk
    if len(safe_chunks) == 0:
        return chunks[:1]

    # ----------- 🔁 RERANKING --------------------------------------------
    pairs = [[question, chunk] for chunk in safe_chunks]
    scores = reranker.predict(pairs)

    ranked_chunks = [
        chunk for _, chunk in sorted(zip(scores, safe_chunks), reverse=True)
    ]

    return ranked_chunks[:3]

#-----------------------------------------------

def generate_answer(question, context):

    prompt = f"""
You are an intelligent AI assistant.

Use the provided context to answer the question.

The answer does NOT need to be an exact sentence from the context.
You are allowed to understand, infer, summarize, and combine information from the context to form a complete answer.

Do NOT use outside knowledge.
Do NOT assume anything.

If the context is related to the question, use it to construct the best possible answer.

Context:
{context}

Question: {question}

Helpful Answer:
"""

    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=512,
    )

    return completion.choices[0].message.content