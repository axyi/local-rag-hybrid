from rag.fts import BM25Index, tokenize

CHUNKS = [
    {"text": "настройка миграций базы данных alembic"},
    {"text": "слой shared в архитектуре FSD"},
    {"text": "правила код ревью и checkpoint"},
    {"text": "использование asyncpg для raw SQL"},
]


def test_tokenize_stemming():
    assert tokenize("миграции") == tokenize("миграций")


def test_tokenize_latin_passthrough():
    assert tokenize("Ruff asyncpg FSD") == ["ruff", "asyncpg", "fsd"]


def test_search_finds_asyncpg_chunk():
    index = BM25Index(CHUNKS)
    result = index.search("когда использовать asyncpg", 3)
    assert result[0] == 3


def test_search_finds_shared_layer_chunk():
    index = BM25Index(CHUNKS)
    result = index.search("что делает слой shared", 2)
    assert result[0] == 1


def test_search_no_positive_score():
    index = BM25Index(CHUNKS)
    assert index.search("квантовая хромодинамика", 5) == []


def test_search_top_n_cap():
    index = BM25Index(CHUNKS)
    result = index.search("миграции алембик база checkpoint asyncpg shared", 1)
    assert len(result) <= 1


def test_empty_index_guard():
    assert BM25Index([]).search("миграции", 5) == []
