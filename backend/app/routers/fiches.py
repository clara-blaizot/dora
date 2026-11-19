from fastapi import APIRouter, HTTPException

from app.routers.deps import resolve_subject
from app.schemas import Fiche, FicheRequest
from app.services import fiches as fiches_service

router = APIRouter(prefix="/subjects", tags=["fiches"])


@router.post("/{subject_id}/fiches", response_model=Fiche)
def creer_fiche(subject_id: str, req: FicheRequest):
    resolve_subject(subject_id)
    try:
        return fiches_service.generer_fiche(subject_id, req.sujet)
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
