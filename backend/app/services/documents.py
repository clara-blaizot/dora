"""Gestion des PDF : copie locale + indexation dans Qdrant.

Les métadonnées sont stockées dans un simple fichier JSON pour commencer ;
on pourra passer à une vraie base de données plus tard.
"""

import json
import uuid

from app.config import DOCUMENTS_INDEX, UPLOAD_DIR
from app.rag import vector_store
from app.rag.pdf import chunk_pages, extract_pages
from app.schemas import Document


class EmptyPdfError(Exception):
    """Le PDF ne contient pas de texte extractible (ex. un scan sans OCR)."""


def _load_index() -> dict[str, dict]:
    if not DOCUMENTS_INDEX.exists():
        return {}
    return json.loads(DOCUMENTS_INDEX.read_text())


def _save_index(index: dict[str, dict]) -> None:
    DOCUMENTS_INDEX.write_text(json.dumps(index, indent=2, ensure_ascii=False))


def add_document(filename: str, content: bytes) -> Document:
    pages = extract_pages(content)
    chunks = chunk_pages(pages)
    if not chunks:
        raise EmptyPdfError(f"{filename} ne contient pas de texte (PDF scanné ?)")

    doc_id = uuid.uuid4().hex
    (UPLOAD_DIR / f"{doc_id}.pdf").write_bytes(content)
    vector_store.index_chunks(doc_id, filename, chunks)

    doc = Document(id=doc_id, filename=filename, nb_pages=len(pages), nb_chunks=len(chunks))
    index = _load_index()
    index[doc_id] = doc.model_dump()
    _save_index(index)
    return doc


def list_documents() -> list[Document]:
    return [Document(**d) for d in _load_index().values()]


def get_documents(doc_ids: list[str]) -> list[Document]:
    """Renvoie les documents demandés, dans l'ordre. Lève KeyError si un id est inconnu."""
    index = _load_index()
    return [Document(**index[doc_id]) for doc_id in doc_ids]


def delete_document(doc_id: str) -> None:
    index = _load_index()
    index.pop(doc_id)
    vector_store.delete_document(doc_id)
    (UPLOAD_DIR / f"{doc_id}.pdf").unlink(missing_ok=True)
    _save_index(index)
