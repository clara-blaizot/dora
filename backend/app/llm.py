"""Point d'accès unique au LLM Gemini."""

from functools import lru_cache

from google import genai

from app.config import MODEL


@lru_cache
def get_client() -> genai.Client:
    # Le client lit GEMINI_API_KEY depuis les variables d'environnement.
    return genai.Client()


def create_message(
    *,
    system: str,
    messages: list[dict],
    max_tokens: int = 16000,
) -> str:
    prompt = "\n\n".join(
        f"{message['role']}:\n{message['content']}"
        for message in messages
    )

    interaction = get_client().interactions.create(
        model=MODEL,
        system_instruction=system,
        input=prompt,
        generation_config={"max_output_tokens": max_tokens},
    )

    return interaction.output_text or ""