"""Questions/réponses sur les PDF (RAG).

1. Recherche : les passages pertinents sont trouvés dans Qdrant, sans LLM.
   Ce sont eux qui sont renvoyés comme sources.
2. Rédaction : le LLM reçoit uniquement ces passages et rédige la réponse.
"""

from app.config import RAG_TOP_K
from app.llm import create_message
from app.rag import vector_store
from app.schemas import ChatResponse, Document, Source

SYSTEM_PROMPT = """Tu es Dora, une assistante qui aide les étudiants à réviser leurs cours.
Réponds en français, de façon claire et pédagogique, en t'appuyant uniquement
sur les extraits de cours fournis. Indique les extraits utilisés avec leur
numéro entre crochets, par exemple [1] ou [2][3]. Si les extraits ne
permettent pas de répondre, dis-le simplement."""


def ask(question: str, documents: list[Document]) -> ChatResponse:
    results = vector_store.search(question, [d.id for d in documents], limit=RAG_TOP_K)
    sources = [
        Source(numero=i, document_id=r.document_id, filename=r.filename, page=r.page, text=r.text, score=r.score)
        for i, r in enumerate(results, start=1)
    ]

    if not sources:
        return ChatResponse(answer="Je n'ai trouvé aucun passage pertinent dans tes cours.", sources=[])

    extraits = "\n\n".join(
        f"[{s.numero}] ({s.filename}, page {s.page})\n{s.text}" for s in sources
    )
    answer = create_message(
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"<extraits>\n{extraits}\n</extraits>\n\nQuestion : {question}",
        }],
    )

    return ChatResponse(answer=answer, sources=sources)