from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_chat_document_inconnu():
    r = client.post("/chat", json={"question": "?", "document_ids": ["inexistant"]})
    assert r.status_code == 404


def test_upload_refuse_non_pdf():
    r = client.post("/documents", files=[("files", ("notes.txt", b"hello", "text/plain"))])
    assert r.status_code == 400
