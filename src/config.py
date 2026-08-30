# Configuration for the hybrid-search knowledge-base assistant

from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
REPO_ROOT = SRC_DIR.parent

# Documents and derived index artifacts live under git-ignored data/
DOCUMENTS_DIR = str(REPO_ROOT / "data" / "corpus")
INDEX_DIR = REPO_ROOT / "data" / "index"
FAISS_INDEX_PATH = str(INDEX_DIR / "index.faiss")
CHUNKS_PATH = str(INDEX_DIR / "chunks.pkl")

# Chunking configuration
CHUNK_SIZE = 700
CHUNK_OVERLAP = 100

# Embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen3:0.6b"
LLM_TIMEOUT = 120.0

# Query expansion (keyword generation)
MAX_KEYWORDS = 6
KEYWORD_TIMEOUT = 15.0

# Hybrid retrieval
TOP_K = 5            # fused chunks handed to the answer LLM
CANDIDATE_POOL = 10  # per-searcher ranking depth fed into RRF
RRF_K = 60           # RRF constant from the assignment formula
