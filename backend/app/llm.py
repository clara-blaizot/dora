"""Point d'accès unique au LLM Gemini."""

import logging
from functools import lru_cache

from google import genai
from google.genai import types
# Erreurs de l'API Interactions : le SDK ne les expose pas dans un module public
from google.genai import _interactions_errors as gemini_errors

from app.config import FALLBACK_MODEL, LLM_TIMEOUT, MODEL

logger = logging.getLogger(__name__)

# Erreurs passagères : 429 (quota), 5xx (modèle surchargé), délai dépassé, réseau
ERREURS_TEMPORAIRES = (
    gemini_errors.RateLimitError,
    gemini_errors.InternalServerError,
    gemini_errors.APIConnectionError,
)


class LLMIndisponible(Exception):
    """Aucun modèle n'a pu répondre (surcharge, quota ou réseau)."""


@lru_cache
def get_client() -> genai.Client:
    # Le client lit GEMINI_API_KEY depuis les variables d'environnement.
    # Sans limite, le SDK réessaie en boucle quand le modèle est surchargé
    # et l'appel semble bloqué : on borne le délai et le nombre d'essais.
    return genai.Client(http_options=types.HttpOptions(
        timeout=LLM_TIMEOUT * 1000,
        retry_options=types.HttpRetryOptions(attempts=2),
    ))


def create_message(
    *,
    system: str,
    messages: list[dict],
    max_tokens: int = 16000,
) -> str:
    """Envoie la requête à MODEL, puis à FALLBACK_MODEL si MODEL est indisponible."""
    prompt = "\n\n".join(
        f"{message['role']}:\n{message['content']}"
        for message in messages
    )

    modeles = [m for m in dict.fromkeys([MODEL, FALLBACK_MODEL]) if m]
    for model in modeles:
        try:
            interaction = get_client().interactions.create(
                model=model,
                system_instruction=system,
                input=prompt,
                generation_config={"max_output_tokens": max_tokens},
            )
            return interaction.output_text or ""
        except ERREURS_TEMPORAIRES as e:
            logger.warning("Modèle %s indisponible : %s", model, e)
            derniere_erreur = e

    raise LLMIndisponible(
        "Le modèle de rédaction est surchargé ou injoignable. Réessaie dans quelques minutes."
    ) from derniere_erreur
