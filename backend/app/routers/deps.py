from fastapi import HTTPException

from app.schemas import Document
from app.services import documents as documents_service


def resolve_documents(doc_ids: list[str]) -> list[Document]:
    try:
        return documents_service.get_documents(doc_ids)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Document inconnu : {e.args[0]}")
