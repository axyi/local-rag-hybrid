from config import MAX_KEYWORDS
from rag import keywords


class FakeResponse:
    def __init__(self, status_code=200, json_data=None, json_error=None):
        self.status_code = status_code
        self._json_data = json_data
        self._json_error = json_error

    def json(self):
        if self._json_error is not None:
            raise self._json_error
        return self._json_data


def _patch_post(monkeypatch, fake_post):
    monkeypatch.setattr(keywords.requests, "post", fake_post)


def test_basic_comma_separated(monkeypatch):
    def fake_post(url, json=None, timeout=None):
        return FakeResponse(json_data={"response": "миграции, alembic, база данных"})

    _patch_post(monkeypatch, fake_post)
    assert keywords.expand_query("вопрос") == ["миграции", "alembic", "база данных"]


def test_think_block_stripped(monkeypatch):
    def fake_post(url, json=None, timeout=None):
        return FakeResponse(json_data={"response": "<think>reasoning here</think>alembic, миграции"})

    _patch_post(monkeypatch, fake_post)
    assert keywords.expand_query("вопрос") == ["alembic", "миграции"]


def test_bullet_list_newlines(monkeypatch):
    def fake_post(url, json=None, timeout=None):
        return FakeResponse(json_data={"response": "- alembic\n- миграции\n"})

    _patch_post(monkeypatch, fake_post)
    assert keywords.expand_query("вопрос") == ["alembic", "миграции"]


def test_cap_and_dedup(monkeypatch):
    raw = "one, two, One, three, four, two, five, six"

    def fake_post(url, json=None, timeout=None):
        return FakeResponse(json_data={"response": raw})

    _patch_post(monkeypatch, fake_post)
    result = keywords.expand_query("вопрос")
    assert result == ["one", "two", "three", "four", "five", "six"]
    assert len(result) == MAX_KEYWORDS


def test_drop_question_echo(monkeypatch):
    question = "Как настроить"

    def fake_post(url, json=None, timeout=None):
        return FakeResponse(json_data={"response": "Как настроить, alembic, КАК НАСТРОИТЬ"})

    _patch_post(monkeypatch, fake_post)
    assert keywords.expand_query(question) == ["alembic"]


def test_timeout_returns_empty(monkeypatch):
    def fake_post(url, json=None, timeout=None):
        raise keywords.requests.exceptions.Timeout()

    _patch_post(monkeypatch, fake_post)
    assert keywords.expand_query("вопрос") == []


def test_http_error_returns_empty(monkeypatch):
    def fake_post(url, json=None, timeout=None):
        return FakeResponse(status_code=500, json_data={"response": "ignored"})

    _patch_post(monkeypatch, fake_post)
    assert keywords.expand_query("вопрос") == []


def test_json_error_returns_empty(monkeypatch):
    def fake_post(url, json=None, timeout=None):
        return FakeResponse(json_error=ValueError("bad json"))

    _patch_post(monkeypatch, fake_post)
    assert keywords.expand_query("вопрос") == []


def test_payload_shape(monkeypatch):
    captured = {}

    def fake_post(url, json=None, timeout=None):
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResponse(json_data={"response": "alembic"})

    _patch_post(monkeypatch, fake_post)
    question = "Как настроить миграции?"
    keywords.expand_query(question)

    payload = captured["json"]
    assert payload["stream"] is False
    assert payload["think"] is False
    assert payload["options"] == {"temperature": 0.0, "num_predict": 100}
    assert captured["timeout"] == 15.0
    assert question in payload["prompt"]
