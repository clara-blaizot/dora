from fastapi import APIRouter, HTTPException

from app.routers.deps import resolve_documents
from app.schemas import Quiz, QuizRequest
from app.services import quiz as quiz_service

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.post("", response_model=Quiz)
def creer_quiz(req: QuizRequest):
    try:
        return quiz_service.generer_quiz(
            resolve_documents(req.document_ids), req.nb_questions, req.sujet
        )
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
