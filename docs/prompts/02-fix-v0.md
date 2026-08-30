# Prompt 02 — fix-v0 post-run reporting corrections

**Stage:** reporting fix-up (no code changes)
**Model:** Claude Sonnet 5 (claude-sonnet-5), via Claude Code CLI

## Prompt

```
go docs/spec/fix-v0.md
```

Per `AGENTS.md` → "go protocol": this invokes the `go` protocol against
`docs/spec/fix-v0.md`, a follow-up spec to spec-v0 that fills in LLM usage
numbers the lab measured post-run from local session transcripts (the
executor cannot measure these itself — the transcripts live outside the
repo root) and aligns the v0 report metrics (spec size in tokens, not lines;
measured token/cost figures replacing the earlier rough estimate).

## Notes

- Verification verdict stated by the spec: an independent re-run of all five
  gates (30 tests, bench reproduced exactly: vector 0.4/0.35 vs hybrid
  0.9/0.68) plus an `ask_llm` live smoke test passed — no code changes were
  requested. All fixes below are reporting-level only.
- Constraint: doc edits only (`docs/llm-usage.md`, `docs/reports/tg-post-v0.md`,
  `README.md`, `docs/reports/report-v0.md`); no touches to `src/`, `tests/`,
  `bench/`, `pyproject.toml` or `uv.lock`. Only `uv run --locked ruff check .`
  was re-run as a sanity gate; the measured token/cost numbers were taken
  verbatim from the spec, not re-derived.
