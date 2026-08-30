# Run report — spec-v0 (hybrid search + query expansion)

**Executor model:** Claude Sonnet 5 (`claude-sonnet-5`), via Claude Code CLI
**Spec:** `docs/spec/spec-v0.md`
**Prompt:** `docs/prompts/01-go-spec-v0.md` (one user prompt: `go docs/spec/spec-v0.md`)
**Run type:** solo single-agent run, committed directly to `main`

## Status

```
STATUS: done
REPAIR CYCLES USED: 0/5
CORPUS COMMIT: f42cc718 verified
```

All five gates of spec section 8 passed on the **first run** — no repair
cycle was needed. Two `fix:`/`test:` commits were added afterward from the
mandatory clean-context code review (REQ-54); those are a separate step from
the REQ-06 repair budget, which covers gate failures during implementation.

## Preconditions (spec section 2)

- Corpus cloned at `larchanka-training/ecto-1-kb`, pinned commit
  `f42cc7181f4bfa6cdf84d2b9ba32de35ab937a5c` — verified via `git rev-parse HEAD`.
- `git check-ignore data/corpus/README.md` → exit 0 (already covered by the
  repo's existing `.gitignore`).
- Local Ollama serving `qwen3:0.6b` — verified via `/api/version` and
  `ollama list`.

## Gates (spec section 8)

| # | Command | Exit | Detail |
|---|---------|------|--------|
| 1 | `uv sync --locked` | 0 | 114 packages resolved, `torch==2.13.0+cpu` |
| 2 | `uv run --locked ruff check .` | 0 | clean |
| 3 | `uv run --locked pytest` | 0 | 30 passed |
| 4 | `uv run --locked python src/main.py build-index` | 0 | 286 chunks / 56 documents |
| 5 | `uv run --locked python src/main.py bench` | 0 | hybrid recall@5=0.9 ≥ 0.6 floor |

## Bench summary

```
vector-only  recall@5=0.4  MRR=0.35
hybrid       recall@5=0.9  MRR=0.68
```

Full table: `docs/assets/bench-v0.md`.

## Deviations from the spec's literal text

Both were surfaced to and resolved by the user during implementation, not
decided unilaterally.

1. **`pyproject.toml`** deviates from REQ-18's verbatim text by two added
   `[tool.ruff.lint.per-file-ignores]` entries ignoring `I001` on
   `src/rag/chunk.py` and `src/rag/embed.py`. REQ-18's verbatim config
   enables ruff's `I` (isort) rule; REQ-17 forbids editing, reformatting, or
   linting those two upstream files. `ruff check .` failed `I001` on exactly
   those two files (their existing import order has third-party imports
   before stdlib) — a genuine spec-internal contradiction with no edit-free
   resolution other than excluding them. Presented to the user as a 3-way
   choice (ignore-list addition / reorder the untouchable files / stop with a
   blocker); the user chose the ignore-list addition as the minimal,
   documented deviation.
2. **`src/rag/query.py`**: one pre-existing line inside `build_prompt` (not
   part of any REQ-29..REQ-34 change) exceeded the verbatim `pyproject.toml`'s
   110-character line length. Wrapped it across two lines — only a newline
   was inserted, no text changed — to satisfy gate 2 without leaving an
   unresolvable contradiction between "keep everything not mentioned here
   as-is" and the mandatory ruff gate.

## Code review (REQ-54)

Ran in a clean context via the `code-reviewer` subagent against
`64ea0f1..HEAD` (before the two follow-up commits below). Verdict: hybrid
retrieval logic (`rag/query.py`, `rag/fts.py`, `rag/fusion.py`,
`rag/keywords.py`) is a correct, verbatim implementation of the spec; all
findings were in test coverage and one dead code path.

| Severity | Finding | Resolution |
|----------|---------|------------|
| 🟡 | `tests/test_hybrid.py` stubs ignored the `top_n` argument, so `retrieve()` passing `TOP_K` instead of `CANDIDATE_POOL` into the hybrid RRF pool would not have been caught | Fixed — stubs now capture and assert `CANDIDATE_POOL`/`TOP_K` |
| 🟡 | `tests/test_keywords.py`'s cap test only exercised `MAX_KEYWORDS` via dedup, never via truncation of distinct items | Fixed — added a duplicate-free 8-item case asserting exactly 6 are returned |
| 🟡 | `src/rag/bench.py`'s `__main__` block crashed (`ModuleNotFoundError`) when run directly — never required by the spec (only `main.py bench` is), and never functional | Fixed — removed |
| 🟢 | `BM25Index` stored an unused `self._corpus_size` | Fixed — simplified to `if not chunks` |
| 🟢 | `run_bench()`'s "every question was processed" check is tautological (no per-question exception handling) | Not changed — REQ-16 forbids adding unrequested error-handling for a scenario (`retrieve()` raising) that the spec's own guarantees (query expansion and BM25 never raise) rule out |

All fixes verified against the full gate sequence (ruff, pytest — 30 passed,
`main.py bench` — unchanged results) before committing.

## Commits

```
d5b1bd5 chore: scaffold uv project (pyproject.toml, uv.lock, python-version)
779de7c test: add hermetic test suite for hybrid retrieval
f3925a4 feat: add query expansion, BM25 full-text search and RRF fusion
84b2a7d fix: repair ingest recursion bug and index path resolution
00ba041 feat: wire hybrid retrieval (vector + BM25 + RRF) into query.py
ce3c0a5 feat: add vector-vs-hybrid retrieval benchmark
6882478 docs: log spec-v0 execution prompt and LLM usage
c4915a1 test: assert CANDIDATE_POOL/TOP_K wiring and a duplicate-free MAX_KEYWORDS cap
6c2992d fix: remove broken bench.py __main__ entry point, dead BM25Index state
```

## Notes for reviewers

- `data/` (corpus + built index) is git-ignored and was never committed, per
  REQ-09 — restore locally with the clone command in spec section 2.
- `docs/llm-usage.md` tokens/cost are now measured: the lab measured them
  post-run from local Claude Code session transcripts (deduplicated by
  request id) — the in-session harness still does not expose these counters
  to the agent directly. See `docs/llm-usage.md` for the figures and
  `docs/reports/tg-post-v0.md` for the public-API-price cost estimate.
