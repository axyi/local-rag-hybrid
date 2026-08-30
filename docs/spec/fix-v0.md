# fix-v0 — post-run reporting corrections

Follow-up prompt to the spec-v0 run. Log it as `docs/prompts/02-fix-v0.md`
per AGENTS.md and apply everything below in **one commit**
(`docs: fill measured LLM usage and align v0 report metrics`).

Verification verdict behind this prompt: the implementation itself passed an
independent re-run of all five gates (30 tests, bench reproduced exactly:
vector 0.4/0.35 vs hybrid 0.9/0.68) plus an `ask_llm` live smoke test — **no
code changes are requested**. All findings are reporting-level.

## Context: measured LLM usage

The lab measured the run from the local Claude Code session transcripts
(`tools/session-usage.py`, deduplicated by request id) — the executor cannot
do this itself (transcripts live outside the repo root). Use these numbers
verbatim; they are the canonical replacement for every `unknown` cell and
rough estimate:

- Main session, `claude-sonnet-5`, 94 API calls, 2026-08-30 14:04–14:37 UTC:
  input 13,012,121 tokens total (190 uncached + 232,672 cache-write +
  12,779,259 cache-read), output 74,968.
- Auxiliary agent sessions (clean-context review fan-out), `claude-opus-4-7`,
  8 sessions / 40 calls inside the same window: input 1,158,640 tokens total
  (80 uncached + 121,313 cache-write + 1,037,247 cache-read), output 18,100.
- Totals: **14,170,761 in (incl. cache reads) / 93,068 out**.
- Cost estimate at Anthropic public API prices (cache write ×1.25 input
  price, cache read ×0.1; sonnet-5 $2/$10 per MTok, opus-4.x $5/$25):
  sonnet ≈ $3.89 + opus ≈ $1.73 = **≈ $5.62** (estimate, harness is
  flat-rate).

## Fixes

1. **`docs/llm-usage.md`** — replace the `unknown` cells: row 1 (sonnet-5
   main session) gets 13.01M in¹ / 74,968 out / ≈$3.89; add row 2
   `review subagents (docs/prompts/01) | claude-opus-4-7 | 1.16M¹ | 18,100 |
   ≈$1.73`; totals row 14.17M¹ / 93,068 / ≈$5.62. Add footnote ¹: input
   includes cache reads (sonnet 12.78M cache-read + 233k cache-write; opus
   1.04M + 121k); cost is an estimate at public API prices per
   `standards/reporting.md` — measured post-run by the lab from local session
   transcripts. Update the Evidence line accordingly.
2. **`docs/reports/tg-post-v0.md`** — two metric corrections, keep everything
   else: (a) the spec size must be stated in tokens, not lines: replace both
   «746 строк» mentions with «9 265 токенов (tiktoken cl100k)»; (b) replace
   the rough token/cost passage («…70.8K токенов (~$0.2); вся сессия целиком —
   грубая оценка ~$5–8») with the measured figures: in/out
   14.17M (с кэш-чтениями) / 93.1k токенов, оценка по публичным API-ценам
   ≈ $5.6 (sonnet-5 ≈ $3.9 + ревью-агенты на opus-4.7 ≈ $1.7), замерено по
   локальным транскриптам сессии. Keep the post under ~1500 characters and in
   Russian.
3. **`README.md`** — fill the Build report headline (replace the *pending*
   sentence): `spec 9 265 tokens · 1 prompt · first run: yes (0/5 repairs) ·
   30 tests · hybrid recall@5 0.9 vs 0.4 vector-only · ≈ $5.6 (estimated at
   public API prices)`.
4. **`docs/reports/report-v0.md`** — in "Notes for reviewers", replace the
   last bullet ("`docs/llm-usage.md` tokens/cost are `unknown` …") with a
   pointer to the now-measured figures in `docs/llm-usage.md` (state that the
   lab measured them post-run from local session transcripts; the in-session
   counters remain unavailable to the agent).

## Constraints

- Doc edits only — do not touch `src/`, `tests/`, `bench/`, `pyproject.toml`
  or `uv.lock`.
- Re-run nothing except `uv run --locked ruff check .` (must stay exit 0) as
  a sanity gate; the numbers above are inputs, not something to re-derive.
- One commit, message body referencing `(prompt: docs/prompts/02-fix-v0.md)`.
  Do not push.
