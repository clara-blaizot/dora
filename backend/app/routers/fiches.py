from fastapi import APIRouter, HTTPException

from app.routers.deps import resolve_documents
from app.schemas import Fiche, FicheRequest
from app.services import fiches as fiches_service

router = APIRouter(prefix="/fiches", tags=["fiches"])


@router.post("", response_model=Fiche)
def creer_fiche(req: FicheRequest):
    try:
        return fiches_service.generer_fiche(resolve_documents(req.document_ids), req.sujet)
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
