"""Génération de quiz (QCM) à partir des PDF.

À implémenter dans la branche `feature/quiz`.
Piste : récupérer les passages de la matière dans Qdrant (`vector_store.search`
sur le sujet, ou tous les morceaux de la matière), puis demander au LLM d'en tirer
des questions, par ex. avec `client.messages.parse(..., output_format=Quiz)`.
"""

from app.schemas import Quiz


def generer_quiz(subject_id: str, nb_questions: int, sujet: str | None = None) -> Quiz:
    raise NotImplementedError("Quiz : pas encore implémenté")
