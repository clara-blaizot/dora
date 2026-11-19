"""Modèles de données échangés entre le frontend et l'API."""

from pydantic import BaseModel, Field


# --- Matières ----------------------------------------------------------------

COULEUR = r"^#[0-9A-Fa-f]{6}$"


class Subject(BaseModel):
    id: str
    name: str
    color: str  # couleur d'affichage, ex. "#D6336C"


class SubjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    color: str = Field(default="#D6336C", pattern=COULEUR)


class SubjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    color: str | None = Field(default=None, pattern=COULEUR)


# --- Documents ---------------------------------------------------------------

class Document(BaseModel):
    id: str
    subject_id: str  # chaque PDF appartient à une seule matière
    filename: str
    nb_pages: int
    nb_chunks: int  # nombre de morceaux indexés dans Qdrant


# --- Questions / réponses ----------------------------------------------------

class AskRequest(BaseModel):
    question: str = Field(min_length=1)


class Source(BaseModel):
    """Un passage de cours retrouvé dans Qdrant."""
    numero: int  # référence [n] utilisée dans la réponse
    document_id: str
    filename: str
    page: int
    text: str
    score: float  # similarité avec la question (cosinus)


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


# --- Fiches de révision ------------------------------------------------------

class FicheRequest(BaseModel):
    sujet: str | None = None  # restreindre la fiche à un chapitre / thème


class Fiche(BaseModel):
    titre: str
    contenu_markdown: str


# --- Quiz --------------------------------------------------------------------

class QuizRequest(BaseModel):
    nb_questions: int = Field(default=10, ge=1, le=50)
    sujet: str | None = None


class QuizQuestion(BaseModel):
    question: str
    choix: list[str]
    bonne_reponse: int  # index dans `choix`
    explication: str


class Quiz(BaseModel):
    titre: str
    questions: list[QuizQuestion]
