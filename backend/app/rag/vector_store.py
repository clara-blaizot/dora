"""Stockage et recherche des morceaux de cours dans Qdrant."""

import uuid
from dataclasses import dataclass
from functools import lru_cache

from qdrant_client import QdrantClient, models

from app.config import QDRANT_COLLECTION, QDRANT_PATH, QDRANT_URL
from app.rag.embeddings import embed, embedding_dim
from app.rag.pdf import Chunk


@dataclass
class SearchResult:
    document_id: str
    filename: str
    page: int
    text: str
    score: float


@lru_cache
def get_client() -> QdrantClient:
    # Serveur Qdrant si QDRANT_URL est défini, sinon stockage local sur disque
    client = QdrantClient(url=QDRANT_URL) if QDRANT_URL else QdrantClient(path=str(QDRANT_PATH))
    _ensure_collection(client)
    return client


def _ensure_collection(client: QdrantClient) -> None:
    if client.collection_exists(QDRANT_COLLECTION):
        return
    client.create_collection(
        QDRANT_COLLECTION,
        vectors_config=models.VectorParams(size=embedding_dim(), distance=models.Distance.COSINE),
    )
    if QDRANT_URL:  # les index de payload n'existent qu'en mode serveur
        client.create_payload_index(QDRANT_COLLECTION, "document_id", models.PayloadSchemaType.KEYWORD)


def index_chunks(document_id: str, filename: str, chunks: list[Chunk]) -> None:
    vectors = embed([c.text for c in chunks])
    points = [
        models.PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={"document_id": document_id, "filename": filename, "page": c.page, "text": c.text},
        )
        for c, vector in zip(chunks, vectors)
    ]
    get_client().upsert(QDRANT_COLLECTION, points=points)


def search(query: str, document_ids: list[str], limit: int = 5) -> list[SearchResult]:
    """Les `limit` morceaux les plus proches de la question, parmi les documents choisis."""
    response = get_client().query_points(
        QDRANT_COLLECTION,
        query=embed([query])[0],
        query_filter=_documents_filter(document_ids),
        limit=limit,
    )
    return [SearchResult(**p.payload, score=p.score) for p in response.points]


def delete_document(document_id: str) -> None:
    get_client().delete(
        QDRANT_COLLECTION,
        points_selector=models.FilterSelector(filter=_documents_filter([document_id])),
    )


def _documents_filter(document_ids: list[str]) -> models.Filter:
    return models.Filter(
        must=[models.FieldCondition(key="document_id", match=models.MatchAny(any=document_ids))]
    )
