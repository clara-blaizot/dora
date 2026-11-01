"""Extraction du texte des PDF et découpage en morceaux indexables."""

import io
import re
from dataclasses import dataclass

from pypdf import PdfReader

CHUNK_SIZE = 1000  # caractères
CHUNK_OVERLAP = 200


@dataclass
class Chunk:
    text: str
    page: int  # numéro de page (à partir de 1)


def extract_pages(content: bytes) -> list[str]:
    """Texte de chaque page du PDF (une chaîne vide pour une page sans texte)."""
    reader = PdfReader(io.BytesIO(content))
    return [_clean(page.extract_text() or "") for page in reader.pages]


def chunk_pages(pages: list[str], size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[Chunk]:
    """Découpe chaque page en morceaux qui se chevauchent.

    On découpe page par page pour que chaque morceau sache d'où il vient :
    c'est ce numéro de page qui est renvoyé comme source.
    """
    chunks = []
    for page_num, text in enumerate(pages, start=1):
        start = 0
        while start < len(text):
            end = min(start + size, len(text))
            if end < len(text):
                # Couper sur un espace plutôt qu'au milieu d'un mot
                space = text.rfind(" ", start + size // 2, end)
                if space != -1:
                    end = space
            piece = text[start:end].strip()
            if piece:
                chunks.append(Chunk(text=piece, page=page_num))
            if end == len(text):
                break
            start = max(end - overlap, start + 1)
    return chunks


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()
