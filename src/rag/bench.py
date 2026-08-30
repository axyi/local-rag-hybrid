"""Vector-only vs hybrid retrieval benchmark over bench/questions.json."""

import json

from config import REPO_ROOT

RECALL_FLOOR = 0.6
BENCH_PATH = REPO_ROOT / "bench" / "questions.json"
MODES = ("vector", "hybrid")


def _truncate(text: str, length: int = 40) -> str:
    return text if len(text) <= length else text[: length - 1] + "…"


def _first_hit_rank(sources: list[str], expected: list[str]) -> int | None:
    for rank, source in enumerate(sources, start=1):
        if any(source.endswith(suffix) for suffix in expected):
            return rank
    return None


def run_bench() -> int:
    from rag.query import retrieve

    with open(BENCH_PATH, encoding="utf-8") as f:
        questions = json.load(f)

    ranks: dict[str, list[int | None]] = {mode: [] for mode in MODES}
    rows = []
    for q in questions:
        row_ranks = {}
        for mode in MODES:
            result = retrieve(q["question"], mode=mode)
            sources = [c["source"] for c in result]
            rank = _first_hit_rank(sources, q["expected"])
            ranks[mode].append(rank)
            row_ranks[mode] = rank
        rows.append((q["question"], row_ranks))

    metrics = {}
    for mode in MODES:
        mode_ranks = ranks[mode]
        hits = [r for r in mode_ranks if r is not None]
        recall = round(len(hits) / len(mode_ranks), 2)
        mrr = round(sum(1 / r if r is not None else 0.0 for r in mode_ranks) / len(mode_ranks), 2)
        metrics[mode] = {"recall@5": recall, "mrr": mrr}

    lines = ["| # | Question | " + " | ".join(MODES) + " |", "|---|" + "---|" * (1 + len(MODES))]
    for idx, (question, row_ranks) in enumerate(rows, start=1):
        cells = [f"hit@{row_ranks[mode]}" if row_ranks[mode] is not None else "miss" for mode in MODES]
        lines.append(f"| {idx} | {_truncate(question)} | " + " | ".join(cells) + " |")

    lines.append("")
    lines.append("**Summary**")
    for mode in MODES:
        lines.append(f"- {mode}: recall@5={metrics[mode]['recall@5']} MRR={metrics[mode]['mrr']}")

    output = "\n".join(lines)
    print(output)

    out_path = REPO_ROOT / "docs" / "assets" / "bench-v0.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(output + "\n", encoding="utf-8")

    return 0 if len(rows) == len(questions) and metrics["hybrid"]["recall@5"] >= RECALL_FLOOR else 1


if __name__ == "__main__":
    import sys

    sys.exit(run_bench())
