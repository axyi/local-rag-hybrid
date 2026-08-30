import re

import snowballstemmer
from rank_bm25 import BM25Okapi

_stemmer = snowballstemmer.stemmer("russian")


def tokenize(text: str) -> list[str]:
    """Lowercase, split on word characters, stem Russian word forms."""
    return _stemmer.stemWords(re.findall(r"\w+", text.lower()))


class BM25Index:
    def __init__(self, chunks: list[dict]) -> None:
        if not chunks:
            self._bm25 = None
            return
        tokenized = [tokenize(chunk["text"]) for chunk in chunks]
        self._bm25 = BM25Okapi(tokenized)

    def search(self, query: str, top_n: int) -> list[int]:
        if self._bm25 is None:
            return []
        scores = self._bm25.get_scores(tokenize(query))
        ranked = sorted(range(len(scores)), key=lambda i: (-scores[i], i))
        ranked = [i for i in ranked if scores[i] > 0]
        return ranked[:top_n]
