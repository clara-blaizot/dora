from fastapi import APIRouter, HTTPException

from app.llm import LLMIndisponible
from app.routers.deps import resolve_subject
from app.schemas import AskRequest, ChatResponse
from app.services import chat as chat_service

router = APIRouter(prefix="/subjects", tags=["questions"])


@router.post("/{subject_id}/ask", response_model=ChatResponse)
def ask(subject_id: str, req: AskRequest):
    """Répond à partir des seuls PDF de la matière."""
    resolve_subject(subject_id)
    try:
        return chat_service.ask(req.question, subject_id)
    except LLMIndisponible as e:
        raise HTTPException(status_code=503, detail=str(e))
