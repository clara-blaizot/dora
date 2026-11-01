"""Point d'accès unique au LLM.

Le LLM ne sert qu'à rédiger (réponses, fiches, quiz) : la recherche des
passages se fait dans app/rag. Pour changer de fournisseur de LLM, il suffit
de modifier ce fichier.
"""

from functools import lru_cache

import anthropic

from app.config import MODEL


@lru_cache
def get_client() -> anthropic.Anthropic:
    # La clé est lue depuis ANTHROPIC_API_KEY (voir .env.example)
    return anthropic.Anthropic()


def create_message(*, system: str, messages: list[dict], max_tokens: int = 16000, **kwargs):
    """Appelle Claude avec les réglages par défaut de Dora.

    `fallbacks="default"` : si le modèle refuse une requête, l'API la rejoue
    automatiquement sur un modèle de repli.
    """
    return get_client().beta.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
        output_config={"effort": "medium"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        **kwargs,
    )
