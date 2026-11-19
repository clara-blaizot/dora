"""Gestion des matières. Une matière regroupe des PDF ; Dora ne répond qu'à
partir des PDF de la matière interrogée."""

import logging
import uuid

from app.config import SUBJECTS_INDEX
from app.schemas import Subject, SubjectCreate, SubjectUpdate
from app.services import documents as documents_service
from app.storage import JsonStore

logger = logging.getLogger(__name__)
_store = JsonStore(SUBJECTS_INDEX)


def list_subjects() -> list[Subject]:
    return [Subject(**s) for s in _store.load().values()]


def get_subject(subject_id: str) -> Subject:
    """Lève KeyError si la matière est inconnue."""
    return Subject(**_store.load()[subject_id])


def create_subject(data: SubjectCreate) -> Subject:
    subject = Subject(id=uuid.uuid4().hex, **data.model_dump())
    index = _store.load()
    index[subject.id] = subject.model_dump()
    _store.save(index)
    return subject


def update_subject(subject_id: str, data: SubjectUpdate) -> Subject:
    """Lève KeyError si la matière est inconnue."""
    index = _store.load()
    index[subject_id].update(data.model_dump(exclude_none=True))
    _store.save(index)
    return Subject(**index[subject_id])


def delete_subject(subject_id: str) -> None:
    """Supprime la matière et tous ses PDF. Lève KeyError si elle est inconnue."""
    get_subject(subject_id)
    for doc in documents_service.list_documents(subject_id):
        documents_service.delete_document(doc.id)
    index = _store.load()
    index.pop(subject_id)
    _store.save(index)


def migrate_orphan_documents() -> None:
    """Au démarrage : range les PDF sans matière dans une matière « Mes cours »."""
    if not documents_service.has_orphans():
        return
    subject = create_subject(SubjectCreate(name="Mes cours"))
    count = documents_service.assign_orphans(subject.id)
    logger.info("%d PDF sans matière rangés dans « Mes cours »", count)
