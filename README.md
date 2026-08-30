# local-rag-hybrid

Hybrid-search upgrade of [MobilaName/local-rag-mcp](https://github.com/MobilaName/local-rag-mcp) —
a local, privacy-first RAG knowledge-base assistant (FAISS +
SentenceTransformers + Ollama + MCP tools) extended with **LLM query
expansion**, **parallel BM25 full-text search** and **Reciprocal Rank
Fusion**. Built spec-first by AI agents as assignment 4 of the coders.su
AI-development training (cohort Dmc-268).

## What's added on top of upstream

- **Query expansion** — a small local LLM (`qwen3:0.6b`) extracts search
  keywords from the user question before retrieval; on any LLM failure the
  raw query is used as-is (graceful fallback).
- **Parallel full-text search** — BM25 (`rank-bm25` + Russian Snowball
  stemming, so «миграции» matches «миграций») runs concurrently with FAISS
  vector search in a thread pool, adding no latency.
- **Hybrid fusion** — Reciprocal Rank Fusion (k=60) merges both rankings;
  top-K fused chunks feed the answer LLM.
- **Benchmark** — a fixed question set over the course knowledge base
  comparing vector-only vs hybrid retrieval (recall@5, MRR).

## Usage

```bash
uv run --locked python src/main.py               # interactive Q&A
uv run --locked python src/main.py build-index   # (re)build FAISS + chunk store
uv run --locked python src/main.py bench         # vector-only vs hybrid benchmark
```

## Setup

```bash
# 1. Dependencies (Python 3.13, torch comes from the PyTorch CPU index)
uv sync --locked

# 2. Knowledge-base corpus (private course repo — requires GitHub access;
#    data/ is git-ignored and must stay local-only)
gh repo clone larchanka-training/ecto-1-kb data/corpus

# 3. Local LLM
#    install Ollama (https://ollama.com/download), then:
ollama pull qwen3:0.6b
```

`data/` holds private course material (including live credentials in the
corpus) — it is git-ignored and must never be committed or quoted.

## Testing

```bash
uv run --locked ruff check .
uv run --locked pytest
```

## Build report

Built with AI agents under the lab workflow (spec-driven, one prompt = one
commit). Headline: *pending — filled by the v0 run report.*
Full report: [docs/reports/](docs/reports/), token accounting:
[docs/llm-usage.md](docs/llm-usage.md).
