from rag.fusion import rrf


def test_basic_fusion_order():
    assert rrf([[1, 2, 3], [3, 1, 4]]) == [1, 3, 2, 4]


def test_single_ranking_passthrough():
    assert rrf([[7, 8, 9]]) == [7, 8, 9]


def test_empty_rankings():
    assert rrf([]) == []


def test_tie_breaks_by_ascending_doc_id():
    assert rrf([[2], [1]]) == [1, 2]


def test_k_zero_rank_weighting():
    result = rrf([[1], [2, 1]], k=0)
    assert result[0] == 1
