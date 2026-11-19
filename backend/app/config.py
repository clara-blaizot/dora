"""Configuration de l'application, lue depuis les variables d'environnement."""

import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")

MODEL = os.getenv("DORA_MODEL", "gemini-3.8-flash")
# Modèle utilisé si MODEL est surchargé ou injoignable (vide = pas de secours)
FALLBACK_MODEL = os.getenv("DORA_FALLBACK_MODEL", "gemini-3.1-flash-lite")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "60"))  # secondes, par tentative
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

# Stockage local des PDF et de leurs métadonnées
DATA_DIR = BACKEND_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
DOCUMENTS_INDEX = DATA_DIR / "documents.json"

# RAG
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
QDRANT_URL = os.getenv("QDRANT_URL")  # vide = Qdrant local, stocké dans QDRANT_PATH
QDRANT_PATH = DATA_DIR / "qdrant"
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "cours")
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "8"))

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)