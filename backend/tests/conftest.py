"""Fixtures communes : chaque test a ses propres données (dossier temporaire +
Qdrant en mémoire), sans toucher à backend/data ni appeler de LLM."""

import pytest
from qdrant_client import QdrantClient

from app.rag import vector_store
from app.routers import documents as documents_router
from app.services import documents as documents_service
from app.services import subjects as subjects_service


@pytest.fixture(autouse=True)
def donnees_isolees(tmp_path, monkeypatch):
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    monkeypatch.setattr(documents_service._store, "path", tmp_path / "documents.json")
    monkeypatch.setattr(subjects_service._store, "path", tmp_path / "subjects.json")
    monkeypatch.setattr(documents_service, "UPLOAD_DIR", uploads)
    monkeypatch.setattr(documents_router, "UPLOAD_DIR", uploads)

    client = QdrantClient(":memory:")
    vector_store._ensure_collection(client)
    monkeypatch.setattr(vector_store, "get_client", lambda: client)
    return tmp_path


def make_pdf(pages: list[str]) -> bytes:
    """PDF minimal avec une ligne de texte par page (texte ASCII uniquement)."""
    objs = ["<< /Type /Catalog /Pages 2 0 R >>", None,
            "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    kids = []
    for text in pages:
        stream = f"BT /F1 12 Tf 50 700 Td ({text}) Tj ET"
        objs.append(f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream")
        objs.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                    f"/Contents {len(objs)} 0 R /Resources << /Font << /F1 3 0 R >> >> >>")
        kids.append(f"{len(objs)} 0 R")
    objs[1] = f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {len(kids)} >>"

    out, offsets = "%PDF-1.4\n", []
    for i, obj in enumerate(objs, 1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n{obj}\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n"
    out += "".join(f"{o:010d} 00000 n \n" for o in offsets)
    out += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF"
    return out.encode("latin-1")
