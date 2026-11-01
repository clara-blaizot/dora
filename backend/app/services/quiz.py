"""Génération de quiz (QCM) à partir des PDF.

À implémenter dans la branche `feature/quiz`.
Piste : récupérer les passages dans Qdrant (`vector_store.search` sur le
sujet, ou tous les morceaux des documents), puis demander au LLM d'en tirer
des questions, par ex. avec `client.messages.parse(..., output_format=Quiz)`.
"""

from app.schemas import Document, Quiz


def generer_quiz(documents: list[Document], nb_questions: int, sujet: str | None = None) -> Quiz:
    raise NotImplementedError("Quiz : pas encore implémenté")
