"""Tests du RAG, sans clé API : Qdrant tourne en mémoire."""

import pytest
from qdrant_client import QdrantClient

from app.rag import vector_store
from app.rag.pdf import chunk_pages


def test_decoupage_garde_le_numero_de_page():
    pages = ["mot " * 600, "", "court"]
    chunks = chunk_pages(pages, size=1000, overlap=200)

    assert {c.page for c in chunks} == {1, 3}
    assert all(len(c.text) <= 1000 for c in chunks)
    assert chunks[-1].text == "court"


@pytest.fixture
def qdrant_memoire(monkeypatch):
    client = QdrantClient(":memory:")
    vector_store._ensure_collection(client)
    monkeypatch.setattr(vector_store, "get_client", lambda: client)
    return client


def test_recherche_trouve_le_bon_passage(qdrant_memoire):
    from app.rag.pdf import Chunk

    vector_store.index_chunks("bio", "bio.pdf", [
        Chunk("La mitochondrie produit l'énergie de la cellule sous forme d'ATP.", page=4),
        Chunk("Le noyau contient l'ADN de la cellule.", page=2),
    ])
    vector_store.index_chunks("histoire", "histoire.pdf", [
        Chunk("La Révolution française commence en 1789.", page=1),
    ])

    results = vector_store.search("Quel organite fabrique l'ATP ?", ["bio"], limit=2)
    assert results[0].page == 4
    assert all(r.document_id == "bio" for r in results)

    vector_store.delete_document("bio")
    assert vector_store.search("ATP", ["bio"]) == []
