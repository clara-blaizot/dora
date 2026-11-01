from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.config import UPLOAD_DIR
from app.schemas import Document
from app.services import documents as documents_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=list[Document])
async def upload_documents(files: list[UploadFile]):
    docs = []
    for f in files:
        if f.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail=f"{f.filename} n'est pas un PDF")
        try:
            docs.append(documents_service.add_document(f.filename, await f.read()))
        except documents_service.EmptyPdfError as e:
            raise HTTPException(status_code=422, detail=str(e))
    return docs


@router.get("", response_model=list[Document])
def list_documents():
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
