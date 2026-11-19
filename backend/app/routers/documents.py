from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import UPLOAD_DIR
from app.schemas import Document
from app.services import documents as documents_service

# L'import se fait par matière : POST /subjects/{id}/documents
router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[Document])
def list_documents():
    """Tous les PDF, toutes matières confondues."""
    return documents_service.list_documents()


@router.get("/{doc_id}/pdf")
def get_pdf(doc_id: str):
    """Renvoie le PDF original, pour l'afficher à la bonne page dans le frontend."""
    path = UPLOAD_DIR / f"{doc_id}.pdf"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Document inconnu")
    return FileResponse(path, media_type="application/pdf")


@router.delete("/{doc_id}", status_code=204)
def delete_document(doc_id: str):
    try:
        documents_service.delete_document(doc_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Document inconnu")
