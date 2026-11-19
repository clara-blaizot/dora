from fastapi import APIRouter, HTTPException, UploadFile

from app.routers.deps import resolve_subject
from app.schemas import Document, Subject, SubjectCreate, SubjectUpdate
from app.services import documents as documents_service
from app.services import subjects as subjects_service

router = APIRouter(prefix="/subjects", tags=["matières"])


@router.get("", response_model=list[Subject])
def list_subjects():
    return subjects_service.list_subjects()


@router.post("", response_model=Subject, status_code=201)
def create_subject(data: SubjectCreate):
    return subjects_service.create_subject(data)


@router.patch("/{subject_id}", response_model=Subject)
def update_subject(subject_id: str, data: SubjectUpdate):
    resolve_subject(subject_id)
    return subjects_service.update_subject(subject_id, data)


@router.delete("/{subject_id}", status_code=204)
def delete_subject(subject_id: str):
    """Supprime la matière ET tous ses PDF."""
    resolve_subject(subject_id)
    subjects_service.delete_subject(subject_id)


@router.get("/{subject_id}/documents", response_model=list[Document])
def list_subject_documents(subject_id: str):
    resolve_subject(subject_id)
    return documents_service.list_documents(subject_id)


@router.post("/{subject_id}/documents", response_model=list[Document])
async def upload_documents(subject_id: str, files: list[UploadFile]):
    resolve_subject(subject_id)
    docs = []
    for f in files:
        if f.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail=f"{f.filename} n'est pas un PDF")
        try:
            docs.append(documents_service.add_document(subject_id, f.filename, await f.read()))
        except documents_service.EmptyPdfError as e:
            raise HTTPException(status_code=422, detail=str(e))
    return docs
