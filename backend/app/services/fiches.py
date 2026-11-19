"""Génération de fiches de révision à partir des PDF.

À implémenter dans la branche `feature/fiches`.
Piste : récupérer les passages de la matière dans Qdrant (`vector_store.search`
sur le sujet, ou tous les morceaux de la matière), puis demander au LLM de les
mettre en forme, par ex. avec `client.messages.parse(..., output_format=Fiche)`
pour obtenir directement un objet `Fiche` validé.
"""

from app.schemas import Fiche


def generer_fiche(subject_id: str, sujet: str | None = None) -> Fiche:
    raise NotImplementedError("Fiches de révision : pas encore implémenté")
