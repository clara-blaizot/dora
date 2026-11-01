from fastapi import APIRouter

from app.routers.deps import resolve_documents
from app.schemas import ChatRequest, ChatResponse
from app.services import chat as chat_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def ask(req: ChatRequest):
    return chat_service.ask(req.question, resolve_documents(req.document_ids))
