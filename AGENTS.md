# local-rag-hybrid — agent rules

Hybrid-search upgrade (LLM query expansion + parallel BM25 full-text search +
Reciprocal Rank Fusion) of the upstream `MobilaName/local-rag-mcp` local RAG
assistant. Course assignment 4 of the coders.su AI-development training.

Standards summary (self-contained): atomic commits (one prompt → one
commit); review in a clean context; deterministic gates before done.

## Spec

SDD: implementation task → spec first (`docs/spec/spec-vN.md`); the spec is
the contract.

**Spec drift:** architecture/tests/interfaces change → update
`docs/spec/spec-vN.md` same commit.

## Stack

- Language: Python 3.13 (pinned via `.python-version`), uv-managed
- Runtime deps (exact pins in `pyproject.toml`): faiss-cpu,
  sentence-transformers (torch from the PyTorch **CPU** index — never the
  default CUDA wheels), rank-bm25, snowballstemmer, fastmcp, ollama, tiktoken,
  pypdf, python-docx, rich, requests, numpy
- LLM runtime: local Ollama at `http://localhost:11434`, model `qwen3:0.6b`
- Tooling: uv, pytest, ruff
- NEVER add dependencies beyond the allowed list without asking.

## Project layout

- `src/` — the application, upstream layout preserved. New retrieval code
  lives in `src/rag/`.
- `src/mcp/` — upstream MCP server/client pair. **NEVER modify these files or
  reorder their imports**: the local `src/mcp` package shadows the SDK's
  `mcp` package, and `src/mcp/server.py` only works because
  `from fastmcp import FastMCP` executes before its `sys.path` insert.
- `src/assistant.py` — upstream orchestrator, out of scope; do not edit.
- `bench/` — committed benchmark fixture (questions + expected sources).
- `data/` — **git-ignored, local-only**: the private `ecto-1-kb` corpus
  (`data/corpus/`) and derived index artifacts (`data/index/`). The corpus is
  private course material and contains real credentials. NEVER commit it,
  NEVER copy or quote its content into code, docs, prompts, reports or
  commit messages. File *paths* are allowed; file *content* is not.
- `docs/` — spec, prompt logs, reports, llm-usage (see Reporting).
- NEVER read or edit anything above the repository root.

## go protocol

<!-- SYNC: canonical text lives in standards/workflow.md §9 (lab repo); this copy is intentionally self-contained -->

`go docs/spec/spec-v0.md` = execute that spec end-to-end per its Execution
contract: work from the repo root, create the files its tree lists, follow
its implementation order, run its acceptance gates verbatim, respect its
bounded fix loop, log every prompt to `docs/prompts/`, append tokens/cost to
`docs/llm-usage.md`, finish with its report template (or its blocker
template). On a spec-internal contradiction (two requirements that cannot
both hold), surface the options and stop for a decision — or emit the spec's
blocker template when running unattended; NEVER resolve it silently.

## Commit format

- Conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`.
- **One prompt → one commit.** Reference the prompt file in the body:
  `(prompt: docs/prompts/NN-<slug>.md)`.
- NEVER mix results of different prompts in one commit or MR.
<!-- SYNC: canonical text lives in standards/workflow.md §6 (lab repo); this copy is intentionally self-contained -->

## Branch strategy

- One task → one branch: `feat/<slug>`, `fix/<slug>`, `docs/<slug>`.
- Exception: a single-agent run implementing a whole spec end-to-end may
  commit directly to `main`; branches are for parallel or partial work.
- Parallel agent work: **one git worktree per agent**, merge via MR; NEVER two
  agents in one working tree.

## Gates — run before reporting success

<!-- DEFAULT STACK (Python/uv) + project acceptance gates from docs/spec/spec-vN.md. -->

```bash
uv sync --locked
uv run --locked ruff check .
uv run --locked pytest
uv run --locked python src/main.py build-index
uv run --locked python src/main.py bench
```

All five MUST exit 0, run in this order. The last two require the
preconditions listed in the spec (corpus cloned at the pinned commit, Ollama
serving `qwen3:0.6b`); if a precondition is unmet, stop with the spec's
blocker template instead of improvising.

## Review

Code review is performed by the `code-reviewer` subagent
(`.claude/agents/code-reviewer.md`) in its own clean context — NEVER
self-review in the writing context.

## Reporting

Every prompt sent to an LLM is logged in `docs/prompts/` (one file per
prompt), tokens/cost in `docs/llm-usage.md`, run reports in `docs/reports/`.

After each run report, generate `docs/reports/tg-post-vN.md` — a
ready-to-paste Telegram post, written in **Russian**: constraints → result →
metrics (executor model — always named; spec tokens, prompts, first-run,
bugs, tokens in/out, cost — when the harness does not expose tokens/cost,
keep that note and add an estimate at public API prices) → a
link to this project's GitHub repository. Under ~1500 characters.

## Secrets

Secrets live in `.env` (git-ignored). NEVER write secrets into code, docs,
prompts, or reports. This includes everything under `data/` — the corpus
holds real third-party credentials; treat its content as secret.
