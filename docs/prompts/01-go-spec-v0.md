# Prompt 01 — execute spec-v0 end-to-end

**Stage:** implementation (spec execution, single-agent run)
**Model:** Claude Sonnet 5 (claude-sonnet-5), via Claude Code CLI

## Prompt

```
go docs/spec/spec-v0.md
```

Per `AGENTS.md` → "go protocol": this invokes the `go` protocol, i.e. execute
`docs/spec/spec-v0.md` end-to-end per its own Execution contract (section 1) —
work from the repo root, create the files its file tree (section 3) lists,
follow its implementation order (section 6), run its acceptance gates (section
8) verbatim, respect its bounded 5-cycle fix loop, log every LLM prompt to
`docs/prompts/`, append tokens/cost to `docs/llm-usage.md`, and finish with the
report template from section 9.

## Notes

- One clarifying exchange occurred mid-run: `pyproject.toml` (REQ-18,
  verbatim) selects ruff's `I` (isort) rule, and `ruff check .` failed with
  `I001` on `src/rag/chunk.py` / `src/rag/embed.py` — two files REQ-17 forbids
  editing, reformatting, or linting. The user chose to resolve this by adding
  `per-file-ignores` entries for `I001` on those two files rather than
  reordering their imports or reformatting `pyproject.toml` beyond the spec's
  verbatim text. See `docs/reports/report-v0.md` → NOTES for the full
  rationale.
- All five gates of spec section 8 passed on the first run — 0 of the 5
  budgeted repair cycles (REQ-06) were used.
