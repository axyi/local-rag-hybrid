import time

import pytest

import rag.query as query_module


@pytest.fixture
def hybrid_env(monkeypatch):
    monkeypatch.setattr(query_module, "index", object())
    chunks = [{"text": f"c{i}", "source": f"s{i}"} for i in range(6)]
    monkeypatch.setattr(query_module, "chunks", chunks)
    return chunks


def test_fusion_order(monkeypatch, hybrid_env):
    monkeypatch.setattr(query_module, "expand_query", lambda q: [])
    monkeypatch.setattr(query_module, "_vector_ranking", lambda q, n: [0, 1, 2])
    monkeypatch.setattr(query_module, "_fts_ranking", lambda q, k, n: [2, 0, 5])

    result = query_module.retrieve("вопрос")
    assert [c["source"] for c in result] == ["s0", "s2", "s1", "s5"]


def test_parallelism(monkeypatch, hybrid_env):
    def slow_vector(q, n):
        time.sleep(0.25)
        return [0, 1]

    def slow_fts(q, k, n):
        time.sleep(0.25)
        return [1, 0]

    monkeypatch.setattr(query_module, "expand_query", lambda q: [])
    monkeypatch.setattr(query_module, "_vector_ranking", slow_vector)
    monkeypatch.setattr(query_module, "_fts_ranking", slow_fts)

    start = time.monotonic()
    query_module.retrieve("вопрос")
    elapsed = time.monotonic() - start
    assert elapsed < 0.45


def test_fallback_empty_expansion(monkeypatch, hybrid_env):
    captured = {}

    def fake_fts(q, keywords_arg, n):
        captured["keywords"] = keywords_arg
        return [0]

    monkeypatch.setattr(query_module, "expand_query", lambda q: [])
    monkeypatch.setattr(query_module, "_vector_ranking", lambda q, n: [1])
    monkeypatch.setattr(query_module, "_fts_ranking", fake_fts)

    result = query_module.retrieve("вопрос")
    assert captured["keywords"] == []
    assert result


def test_keywords_forwarded(monkeypatch, hybrid_env):
    captured = {}

    def fake_fts(q, keywords_arg, n):
        captured["keywords"] = keywords_arg
        return []

    monkeypatch.setattr(query_module, "expand_query", lambda q: ["alembic"])
    monkeypatch.setattr(query_module, "_vector_ranking", lambda q, n: [])
    monkeypatch.setattr(query_module, "_fts_ranking", fake_fts)

    query_module.retrieve("вопрос")
    assert captured["keywords"] == ["alembic"]


def test_vector_mode_skips_expansion(monkeypatch, hybrid_env):
    def fail_expand(q):
        raise AssertionError("expand_query should not be called in vector mode")

    monkeypatch.setattr(query_module, "expand_query", fail_expand)
    monkeypatch.setattr(query_module, "_vector_ranking", lambda q, n: [3, 4])

    result = query_module.retrieve("вопрос", mode="vector")
    assert [c["source"] for c in result] == ["s3", "s4"]
