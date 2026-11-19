"""Tests de la rédaction, sans appel réel à Gemini (client simulé)."""

from types import SimpleNamespace

import httpx2
import pytest
from fastapi.testclient import TestClient

from app import llm
from app.main import app
from app.rag.vector_store import SearchResult
from app.schemas import Document
from app.services import chat as chat_service


def _erreur_503():
    response = httpx2.Response(503, request=httpx2.Request("POST", "https://gemini.test"))
    return llm.gemini_errors.InternalServerError("surchargé", response=response, body=None)


class FauxClient:
    """Simule Gemini : chaque modèle renvoie un texte ou lève une erreur."""

    def __init__(self, reponses: dict):
        self.reponses = reponses
        self.appels = []
        self.interactions = SimpleNamespace(create=self._create)

    def _create(self, *, model, **kwargs):
        self.appels.append(model)
        reponse = self.reponses[model]
        if isinstance(reponse, Exception):
            raise reponse
        return SimpleNamespace(output_text=reponse)


@pytest.fixture
def faux_gemini(monkeypatch):
    monkeypatch.setattr(llm, "MODEL", "principal")
    monkeypatch.setattr(llm, "FALLBACK_MODEL", "secours")

    def installer(reponses):
        client = FauxClient(reponses)
        monkeypatch.setattr(llm, "get_client", lambda: client)
        return client

    return installer


def _appeler():
    return llm.create_message(system="s", messages=[{"role": "user", "content": "q"}])


def test_modele_principal(faux_gemini):
    client = faux_gemini({"principal": "bonjour", "secours": "inutile"})
    assert _appeler() == "bonjour"
    assert client.appels == ["principal"]


def test_secours_si_modele_surcharge(faux_gemini):
    client = faux_gemini({"principal": _erreur_503(), "secours": "bonjour"})
    assert _appeler() == "bonjour"
    assert client.appels == ["principal", "secours"]


def test_erreur_claire_si_tout_est_surcharge(faux_gemini):
    faux_gemini({"principal": _erreur_503(), "secours": _erreur_503()})
    with pytest.raises(llm.LLMIndisponible):
        _appeler()


def test_reponse_vide_remplacee(monkeypatch):
    resultat = SearchResult(document_id="d", filename="cours.pdf", page=1, text="t", score=0.5)
    monkeypatch.setattr(chat_service.vector_store, "search", lambda *a, **k: [resultat])
    monkeypatch.setattr(chat_service, "create_message", lambda **k: "  ")

    doc = Document(id="d", filename="cours.pdf", nb_pages=1, nb_chunks=1)
    reponse = chat_service.ask("question", [doc])

    assert "pas réussi" in reponse.answer
    assert len(reponse.sources) == 1


def test_route_chat_renvoie_503(monkeypatch):
    doc = Document(id="d", filename="cours.pdf", nb_pages=1, nb_chunks=1)
    monkeypatch.setattr("app.routers.chat.resolve_documents", lambda ids: [doc])

    def indisponible(question, documents):
        raise llm.LLMIndisponible("surchargé")

    monkeypatch.setattr(chat_service, "ask", indisponible)

    r = TestClient(app).post("/chat", json={"question": "?", "document_ids": ["d"]})
    assert r.status_code == 503
    assert r.json()["detail"] == "surchargé"
