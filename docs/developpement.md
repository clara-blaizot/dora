# Guide de développement

## Prérequis

- Python 3.11 ou plus (testé avec 3.14)
- Node 20 ou plus
- Une clé API Anthropic (seulement pour la rédaction des réponses, les tests n'en ont pas besoin)
- Optionnel : Docker, pour Qdrant en mode serveur

## Installation

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # renseigner ANTHROPIC_API_KEY
uvicorn app.main:app --reload
```

Dans VS Code, sélectionnez `backend/.venv` comme interpréteur Python
(commande « Python: Select Interpreter »).

### Frontend

```bash
cd frontend
npm install
npm run dev                 # http://localhost:5173
```

### Qdrant serveur (optionnel)

```bash
docker compose up -d        # à la racine du projet
# puis dans backend/.env :  QDRANT_URL=http://localhost:6333
```

Tableau de bord : http://localhost:6333/dashboard

## Variables d'environnement (`backend/.env`)

| Variable | Défaut | Rôle |
|---|---|---|
| `ANTHROPIC_API_KEY` | – | clé de l'API Claude |
| `DORA_MODEL` | `claude-opus-5-5` | modèle de rédaction ([llm.md](llm.md)) |
| `FRONTEND_ORIGIN` | `http://localhost:5173` | origine autorisée (CORS) |
| `EMBEDDING_MODEL` | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | modèle d'embeddings ([rag.md](rag.md)) |
| `QDRANT_URL` | vide (mode local) | adresse d'un serveur Qdrant |
| `QDRANT_COLLECTION` | `cours` | nom de la collection |
| `RAG_TOP_K` | `5` | nombre de passages par question |

## Tests

```bash
cd backend
pytest
```

| Fichier | Ce qui est testé |
|---|---|
| `tests/test_api.py` | santé, document inconnu (404), refus des fichiers non PDF |
| `tests/test_rag.py` | découpage par page, recherche filtrée, suppression (Qdrant en mémoire) |

Au premier lancement, le modèle d'embeddings est téléchargé, ce qui prend
environ une minute.

## Travailler à deux avec git

- `main` doit toujours fonctionner. On n'y pousse pas directement.
- Une branche par sujet : `feature/fiches`, `feature/quiz`, `fix/…`, `docs/…`
- On fusionne par Pull Request, relue par l'autre personne.

```bash
git checkout main && git pull
git checkout -b feature/quiz
# … travail, commits …
git push -u origin feature/quiz      # puis ouvrir la PR sur GitHub
```

## Ajouter une fonctionnalité (checklist)

1. **Schémas** : requête et réponse dans `backend/app/schemas.py`.
2. **Service** : `backend/app/services/<nom>.py`. Récupérer les passages avec
   `app.rag.vector_store`, rédiger avec `app.llm`.
3. **Route** : `backend/app/routers/<nom>.py`, à enregistrer dans `main.py`.
4. **Tests** : `backend/tests/`.
5. **Frontend** : une fonction dans `api.js` et un composant dans `components/`.
6. **Docs** : mettre à jour [api.md](api.md), la page concernée, et
   [decisions.md](decisions.md) si un choix technique a été fait.
