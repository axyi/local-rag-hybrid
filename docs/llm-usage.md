# LLM usage

| # | Stage | Model | Tokens in | Tokens out | Cost |
|---|-------|-------|-----------|------------|------|
| 1 | implementation (prompt: docs/prompts/01-go-spec-v0.md) | Claude Sonnet 5 (claude-sonnet-5) | 13.01M¹ | 74,968 | ≈$3.89 |
| 2 | review subagents (docs/prompts/01) | claude-opus-4-7 | 1.16M¹ | 18,100 | ≈$1.73 |
| **Σ** | | | 14.17M¹ | 93,068 | ≈$5.62 |

¹ input includes cache reads (sonnet 12.78M cache-read + 233k cache-write;
opus 1.04M cache-read + 121k cache-write); cost is an estimate at public API
prices per `standards/reporting.md` — measured post-run by the lab from local
session transcripts.

Evidence: measured post-run by the lab from local Claude Code session
transcripts (`tools/session-usage.py`, deduplicated by request id) — the
in-session harness does not expose per-session token/cost counters to the
agent directly; cost is a public-API-price estimate (see footnote ¹).
