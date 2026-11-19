"""Gestion des PDF : copie locale + indexation dans Qdrant.

Chaque PDF appartient à une matière (`subject_id`).
"""

import uuid

from app.config import DOCUMENTS_INDEX, UPLOAD_DIR
from app.rag import vector_store
from app.rag.pdf import chunk_pages, extract_pages
from app.schemas import Document
from app.storage import JsonStore

_store = JsonStore(DOCUMENTS_INDEX)


class EmptyPdfError(Exception):
    """Le PDF ne contient pas de texte extractible (ex. un scan sans OCR)."""


def add_document(subject_id: str, filename: str, content: bytes) -> Document:
    pages = extract_pages(content)
    chunks = chunk_pages(pages)
    if not chunks:
        raise EmptyPdfError(f"{filename} ne contient pas de texte (PDF scanné ?)")

    doc_id = uuid.uuid4().hex
    (UPLOAD_DIR / f"{doc_id}.pdf").write_bytes(content)
    vector_store.index_chunks(doc_id, subject_id, filename, chunks)

    doc = Document(id=doc_id, subject_id=subject_id, filename=filename, nb_pages=len(pages), nb_chunks=len(chunks))
    index = _store.load()
    index[doc_id] = doc.model_dump()
    _store.save(index)
    return doc


def list_documents(subject_id: str | None = None) -> list[Document]:
    docs = [Document(**d) for d in _store.load().values()]
    if subject_id is not None:
        docs = [d for d in docs if d.subject_id == subject_id]
    return docs


def delete_document(doc_id: str) -> None:
    """Lève KeyError si le document est inconnu."""
    index = _store.load()
    index.pop(doc_id)
    vector_store.delete_document(doc_id)
    (UPLOAD_DIR / f"{doc_id}.pdf").unlink(missing_ok=True)
    _store.save(index)


def assign_orphans(subject_id: str) -> int:
    """Range dans `subject_id` les PDF importés avant l'existence des matières.

    Renvoie le nombre de PDF déplacés.
    """
    index = _store.load()
    orphans = [doc_id for doc_id, d in index.items() if not d.get("subject_id")]
    for doc_id in orphans:
        vector_store.set_subject(doc_id, subject_id)
        index[doc_id]["subject_id"] = subject_id
    if orphans:
        _store.save(index)
    return len(orphans)


def has_orphans() -> bool:
    return any(not d.get("subject_id") for d in _store.load().values())
