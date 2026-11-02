# Dora

Assistante IA qui aide les étudiants à réviser leurs cours à partir de leurs PDF.

- **Questions sur les cours :** Dora retrouve les passages pertinents (RAG avec
  Qdrant, sans LLM), puis rédige la réponse en citant ses sources (fichier, page, extrait).
- **Fiches de révision** 🚧
- **Quiz** 🚧

## Démarrage rapide

```bash
# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # renseigner GEMINI_API_KEY
uvicorn app.main:app --reload # http://localhost:8000/docs

# Frontend (autre terminal)
cd frontend
npm install
npm run dev                   # http://localhost:5173
```

Le backend lit la clé API depuis `backend/.env` via `GEMINI_API_KEY` et utilise
le modèle défini par `DORA_MODEL` (par défaut : `gemini-3.8-flash`).

## Documentation

Toute la documentation est dans [`docs/`](docs/README.md) :

- [Architecture](docs/architecture.md)
- [RAG (recherche des passages)](docs/rag.md)
- [LLM (rédaction, modèles)](docs/llm.md)
- [API](docs/api.md)
- [Frontend](docs/frontend.md)
- [Guide de développement](docs/developpement.md)
- [Journal des décisions](docs/decisions.md)
