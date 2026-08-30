from pathlib import Path

import rag.ingest as ingest_module


def _build_corpus(tmp_path):
    (tmp_path / "a.md").write_text("hello", encoding="utf-8")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "b.txt").write_text("world", encoding="utf-8")
    deep = sub / "deep"
    deep.mkdir()
    (deep / "c.bin").write_bytes(b"\x00\x01")
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "d.md").write_text("internal", encoding="utf-8")
    return tmp_path


def test_ingest_documents_count(tmp_path, monkeypatch):
    _build_corpus(tmp_path)
    monkeypatch.setattr(ingest_module, "DOCUMENTS_DIR", str(tmp_path))

    docs = ingest_module.ingest_documents()
    assert len(docs) == 2


def test_ingest_excludes_unsupported_and_hidden(tmp_path, monkeypatch):
    _build_corpus(tmp_path)
    monkeypatch.setattr(ingest_module, "DOCUMENTS_DIR", str(tmp_path))

    docs = ingest_module.ingest_documents()
    names = {Path(d["path"]).name for d in docs}
    assert "c.bin" not in names
    assert not any(".git" in d["path"] for d in docs)


def test_ingest_document_shape(tmp_path, monkeypatch):
    _build_corpus(tmp_path)
    monkeypatch.setattr(ingest_module, "DOCUMENTS_DIR", str(tmp_path))

    docs = ingest_module.ingest_documents()
    for doc in docs:
        assert doc["path"]
        assert doc["text"]
