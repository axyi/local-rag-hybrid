import pickle
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import faiss
import requests
from sentence_transformers import SentenceTransformer

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    CANDIDATE_POOL,
    CHUNKS_PATH,
    EMBEDDING_MODEL,
    FAISS_INDEX_PATH,
    LLM_TIMEOUT,
    OLLAMA_MODEL,
    OLLAMA_URL,
    RRF_K,
    TOP_K,
)
from rag.fts import BM25Index
from rag.fusion import rrf
from rag.keywords import expand_query

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


# Global variables for index and chunks
index = None
chunks = []
bm25 = None


def _ensure_index_exists():
    """Ensure FAISS index exists, build it if it doesn't."""
    global index, chunks, bm25

    index_path = Path(FAISS_INDEX_PATH)
    chunks_path = Path(CHUNKS_PATH)

    # Check if index exists
    if index_path.exists() and chunks_path.exists():
        try:
            index = faiss.read_index(str(index_path))
            with open(chunks_path, "rb") as f:
                chunks = pickle.load(f)
            bm25 = BM25Index(chunks)
            return True
        except Exception as e:
            print(f"⚠️  Warning: Error loading existing index: {e}")
            print("Rebuilding index...")

    # Index doesn't exist or failed to load, build it
    print("📦 Index not found. Building index from documents...")
    try:
        from rag.build_index import build_index
        build_index()

        # Load the newly created index
        if index_path.exists() and chunks_path.exists():
            index = faiss.read_index(str(index_path))
            with open(chunks_path, "rb") as f:
                chunks = pickle.load(f)
            bm25 = BM25Index(chunks)
            print("✅ Index built and loaded successfully")
            return True
        else:
            print("❌ Failed to build index. No documents found or error occurred.")
            from config import DOCUMENTS_DIR
            print(f"   Check that documents exist in: {DOCUMENTS_DIR}")
            return False
    except Exception as e:
        print(f"❌ Error building index: {e}")
        import traceback
        traceback.print_exc()
        return False


def _vector_ranking(query: str, top_n: int) -> list[int]:
    q_emb = _get_model().encode([query])
    faiss.normalize_L2(q_emb)
    _scores, ids = index.search(q_emb, top_n)
    return [int(i) for i in ids[0] if i != -1]


def _fts_ranking(query: str, keywords: list[str], top_n: int) -> list[int]:
    if bm25 is None:
        return []
    return bm25.search(" ".join([query, *keywords]), top_n)


def retrieve(query: str, mode: str = "hybrid"):
    """Retrieve relevant chunks; mode is "hybrid" or "vector"."""
    if index is None or len(chunks) == 0:
        if not _ensure_index_exists():
            return []
    if mode == "vector":
        return [chunks[i] for i in _vector_ranking(query, TOP_K)]
    keywords = expand_query(query)
    with ThreadPoolExecutor(max_workers=2) as pool:
        vec_future = pool.submit(_vector_ranking, query, CANDIDATE_POOL)
        fts_future = pool.submit(_fts_ranking, query, keywords, CANDIDATE_POOL)
        vec_ids = vec_future.result()
        fts_ids = fts_future.result()
    fused = rrf([vec_ids, fts_ids], k=RRF_K)
    return [chunks[i] for i in fused[:TOP_K]]


def build_prompt(query, contexts):
    """Build prompt with retrieved context."""
    if not contexts:
        return f"""
<role>You are a helpful assistant that answers questions about company information.</role>
<instructions>Answer the question based on your general knowledge. If you don't know, say so.</instructions>

<query>
{query}
</query>

<assistant>
"""

    context_text = "\n\n".join(
        f"[Source: {c['source']}]\n{c['text']}"
        for c in contexts
    )

    return f"""
<role>You are a helpful assistant that answers questions about company information.</role>
<instructions>Answer the question ONLY based on the context provided below. If the answer is not
in the context, say "I don't have that information in the knowledge base."</instructions>

<context>
{context_text}
</context>

<query>
{query}
</query>

<assistant>
"""


def ask_llm(prompt):
    """Query Ollama LLM."""
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "think": False
        },
        timeout=LLM_TIMEOUT
    )
    raw = response.json()["response"]
    return re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)


def ask(query: str):
    """Answer a question using RAG."""
    contexts = retrieve(query)
    prompt = build_prompt(query, contexts)
    return ask_llm(prompt), contexts


if __name__ == "__main__":
    while True:
        q = input("\n❓ Question: ")
        if q.lower() in {"exit", "quit"}:
            break
        print("\n🤖 Answer:\n")
        answer, sources = ask(q)
        print(answer)
        if sources:
            print("\n📚 Sources:")
            for src in sources:
                print(f"  - {src['source']}")
