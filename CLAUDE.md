# Dora

Assistante de révision : FastAPI (`backend/`) + React/Vite (`frontend/`), RAG avec Qdrant.
Vue d'ensemble : `docs/architecture.md`.

## Règles

- La documentation est en français, dans `docs/`. Toute modification de
  comportement, de route, de configuration ou de choix technique met à jour la
  page concernée dans le même changement. Un choix technique ajoute aussi une
  entrée datée en haut de `docs/decisions.md`.
- La recherche des passages (`app/rag/`) n'utilise jamais de LLM. Le LLM
  (`app/llm.py`) sert uniquement à rédiger.
- Tests : `cd backend && .venv/bin/pytest`
