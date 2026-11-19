from fastapi import APIRouter, HTTPException

from app.llm import LLMIndisponible
from app.routers.deps import resolve_documents
from app.schemas import ChatRequest, ChatResponse
from app.services import chat as chat_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def ask(req: ChatRequest):
    documents = resolve_documents(req.document_ids)
    try:
        return chat_service.ask(req.question, documents)
    except LLMIndisponible as e:
        raise HTTPException(status_code=503, detail=str(e))
