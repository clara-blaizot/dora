from fastapi import HTTPException

from app.schemas import Subject
from app.services import subjects as subjects_service


def resolve_subject(subject_id: str) -> Subject:
    try:
        return subjects_service.get_subject(subject_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Matière inconnue")
