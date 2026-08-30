"""Reciprocal Rank Fusion of multiple ranked doc-id lists."""


def rrf(rankings: list[list[int]], k: int = 60) -> list[int]:
    """Fuse ranked doc-id lists via Reciprocal Rank Fusion."""
    scores: dict[int, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores, key=lambda d: (-scores[d], d))
