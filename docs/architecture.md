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
│   │   ├── storage.py         JsonStore : petit stockage dans un fichier JSON
│   │   ├── schemas.py         modèles Pydantic des requêtes / réponses
│   │   ├── llm.py             client du LLM (seul fichier qui parle au LLM)
│   │   ├── rag/
│   │   │   ├── pdf.py         extraction du texte + découpage en morceaux
│   │   │   ├── embeddings.py  texte → vecteurs (fastembed, local)
│   │   │   └── vector_store.py indexation / recherche / suppression dans Qdrant
│   │   ├── routers/           couche HTTP : valide, appelle un service, gère les erreurs
│   │   │   ├── deps.py        resolve_subject : 404 si la matière est inconnue
│   │   │   ├── subjects.py    CRUD des matières + import de PDF dans une matière
│   │   │   ├── documents.py   chat.py   fiches.py   quiz.py
│   │   └── services/          logique métier, une par fonctionnalité
│   │       ├── subjects.py    documents.py   chat.py   fiches.py   quiz.py
│   ├── data/                  (ignoré par git) PDF, index JSON, Qdrant local
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/
│       ├── api.js             tous les appels au backend
│       ├── App.jsx            état global + mise en page (matières, chat, sources, cours)
│       ├── hooks/             useSubjects : charge / crée les matières via l'API
│       └── components/        Sidebar, ChatPanel, SourcesPanel, CoursesBar
├── docs/                      cette documentation
├── dora-maquette.html         maquette de référence du frontend
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

1. Le frontend envoie `POST /subjects/{id}/ask` avec `{question}` pour la matière affichée.
2. `routers/chat.py` vérifie que la matière existe (`deps.resolve_subject`).
3. `services/chat.py` appelle `vector_store.search(question, subject_id)`.
4. Qdrant renvoie les `RAG_TOP_K` morceaux les plus proches **parmi ceux de la
   matière** (filtre `subject_id`). Ce sont les **sources**.
5. Ces sources sont numérotées [1]…[n] et envoyées au LLM avec la question.
6. Le LLM rédige la réponse en citant les numéros.
7. Le backend renvoie `{answer, sources}` et le frontend affiche les deux.

## Stockage

| Donnée | Où | Format |
|---|---|---|
| PDF originaux | `backend/data/uploads/<id>.pdf` | fichier |
| Matières | `backend/data/subjects.json` | JSON `{id: Subject}` |
| Liste des documents | `backend/data/documents.json` | JSON `{id: Document}` (avec `subject_id`) |
| Morceaux + vecteurs | Qdrant, collection `cours` | points avec payload `document_id, subject_id, filename, page, text` |

Une matière regroupe des PDF ; un PDF appartient à une seule matière. Au
démarrage, `migrate_orphan_documents` range les PDF importés avant
l'existence des matières dans une matière « Mes cours ».

Les fichiers JSON sont volontairement simples. On le remplacera par une base de
données (SQLite par exemple) quand il y aura des comptes utilisateurs.
