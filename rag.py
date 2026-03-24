from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import ollama
from pypdf import PdfReader

# 🔹 Load PDF
def load_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


# 🔹 Chunking
def chunk_text(text, chunk_size=500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


# Load data
text = load_pdf("policy.pdf")
chunks = chunk_text(text)

# 🔹 Embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(chunks)

# 🔹 FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

# 🔹 Cache
cache = {}

# 🔹 RAG function with history
def get_answer(query, history=None):

    # ✅ Check cache
    if query in cache:
        return cache[query]

    query_embedding = model.encode([query])
    distances, indices = index.search(np.array(query_embedding), k=3)

    selected_chunks = [chunks[i] for i in indices[0]]
    context = "\n\n".join(selected_chunks)

    history_text = ""
    if history:
        history_text = "\n".join(history)

    prompt = f"""
You are a professional assistant.

Rules:
- Answer ONLY from context
- If answer not found, say "Not available in document"
- Keep answer clear and concise

Conversation History:
{history_text}

Context:
{context}

Question:
{query}

Answer:
"""

    response = ollama.chat(
        model="phi3",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response['message']['content']

    # 🔥 Add source snippets
    sources = "\n\n---\n📄 Source:\n" + "\n\n".join(selected_chunks[:2])

    final_answer = answer + sources

    # ✅ Store in cache
    cache[query] = final_answer

    return final_answer


# 🔹 Summarize function
def summarize_text(text):
    prompt = f"""
Summarize the following text in 3-5 bullet points:

{text}
"""
    response = ollama.chat(
        model="phi3",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['message']['content']