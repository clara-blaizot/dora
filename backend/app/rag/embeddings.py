"""Calcul des embeddings, en local avec fastembed (pas d'API, gratuit).

Le modèle est téléchargé automatiquement au premier appel.
Changer de modèle impose de réindexer les PDF (la dimension des vecteurs change).
"""

from functools import lru_cache

from fastembed import TextEmbedding

from app.config import EMBEDDING_MODEL


@lru_cache
def _model() -> TextEmbedding:
    return TextEmbedding(EMBEDDING_MODEL)


def embedding_dim() -> int:
    return _model().embedding_size


def embed(texts: list[str]) -> list[list[float]]:
    return [v.tolist() for v in _model().embed(texts)]
