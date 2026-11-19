from fastapi import APIRouter, HTTPException

from app.routers.deps import resolve_subject
from app.schemas import Quiz, QuizRequest
from app.services import quiz as quiz_service

router = APIRouter(prefix="/subjects", tags=["quiz"])


@router.post("/{subject_id}/quiz", response_model=Quiz)
def creer_quiz(subject_id: str, req: QuizRequest):
    resolve_subject(subject_id)
    try:
        return quiz_service.generer_quiz(subject_id, req.nb_questions, req.sujet)
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
