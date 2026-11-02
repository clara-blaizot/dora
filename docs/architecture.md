# Architecture

## Vue d'ensemble

```
┌──────────────┐   HTTP/JSON   ┌───────────────────────────────────────────┐
│  Frontend    │ ────────────► │  Backend (FastAPI)                        │
│  React/Vite  │               │                                           │
│  :5173       │ ◄──────────── │  routers/  →  services/  →  rag/  → Qdrant│
└──────────────┘               │                          →  llm.py → Gemini │
                               │  :8000                                     │
                               └───────────────────────────────────────────┘
```

Le projet repose sur un principe central : **la recherche des passages et la
rédaction sont séparées.**

- **Recherche (`app/rag/`)** : elle trouve les passages de cours pertinents
  par similarité de vecteurs dans Qdrant, sans aucun LLM. Ces passages sont
  les sources montrées à l'étudiant.
- **Rédaction (`app/llm.py`)** : le LLM reçoit uniquement ces passages et
  rédige la réponse, la fiche ou le quiz.

## Arborescence

```
dora/
├── backend/
│   ├── app/
│   │   ├── main.py            crée l'app FastAPI, CORS, enregistre les routers
│   │   ├── config.py          variables d'environnement et chemins
│   │   ├── schemas.py         modèles Pydantic des requêtes / réponses
│   │   ├── llm.py             client du LLM (seul fichier qui parle au LLM)
│   │   ├── rag/
│   │   │   ├── pdf.py         extraction du texte + découpage en morceaux
│   │   │   ├── embeddings.py  texte → vecteurs (fastembed, local)
│   │   │   └── vector_store.py indexation / recherche / suppression dans Qdrant
│   │   ├── routers/           couche HTTP : valide, appelle un service, gère les erreurs
│   │   │   ├── deps.py        résolution des document_ids (404 si inconnu)
│   │   │   ├── documents.py   chat.py   fiches.py   quiz.py
│   │   └── services/          logique métier, une par fonctionnalité
│   │       ├── documents.py   chat.py   fiches.py   quiz.py
│   ├── data/                  (ignoré par git) PDF, index JSON, Qdrant local
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/
│       ├── api.js             tous les appels au backend
│       ├── App.jsx            mise en page + onglets
│       └── components/
├── docs/                      cette documentation
└── docker-compose.yml         Qdrant serveur (optionnel)
```

## Découpage en couches (backend)

| Couche | Rôle | Ne fait pas |
|---|---|---|
| `routers/` | HTTP : paramètres, codes d'erreur | de logique métier |
| `services/` | logique d'une fonctionnalité | de HTTP (pas de `HTTPException`) |
| `rag/` | texte, vecteurs, Qdrant | d'appel au LLM |
| `llm.py` | appel au LLM | de recherche |

Les services lèvent des exceptions Python (`KeyError`, `EmptyPdfError`,
`NotImplementedError`), et les routers les traduisent en codes HTTP.

## Parcours d'une question

1. Le frontend envoie `POST /chat` avec `{question, document_ids}`.
2. `routers/chat.py` vérifie que les documents existent (`deps.resolve_documents`).
3. `services/chat.py` appelle `vector_store.search(question, document_ids)`.
4. Qdrant renvoie les `RAG_TOP_K` morceaux les plus proches. Ce sont les **sources**.
5. Ces sources sont numérotées [1]…[n] et envoyées au LLM avec la question.
6. Le LLM rédige la réponse en citant les numéros.
7. Le backend renvoie `{answer, sources}` et le frontend affiche les deux.

## Stockage

| Donnée | Où | Format |
|---|---|---|
| PDF originaux | `backend/data/uploads/<id>.pdf` | fichier |
| Liste des documents | `backend/data/documents.json` | JSON `{id: Document}` |
| Morceaux + vecteurs | Qdrant, collection `cours` | points avec payload `document_id, filename, page, text` |

Le fichier JSON est volontairement simple. On le remplacera par une base de
données (SQLite par exemple) quand il y aura des comptes utilisateurs.
