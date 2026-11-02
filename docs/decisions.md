# Journal des décisions

Chaque choix technique important, avec sa raison. Les entrées les plus
récentes sont en haut. Pour revenir sur une décision, ajoutez une nouvelle
entrée plutôt que d'effacer l'ancienne.

---

## 2026-11-01 — Documentation dans `docs/`

**Décision :** la documentation est écrite en Markdown dans `docs/`, une page
par sujet, et mise à jour dans la même PR que le code.
**Pourquoi :** elle est lisible directement sur GitHub et versionnée avec le code.

## 2026-11-01 — Qdrant local par défaut, serveur en option

**Décision :** sans `QDRANT_URL`, Qdrant tourne en mode local (fichiers dans
`backend/data/qdrant`). Un `docker-compose.yml` permet de lancer un serveur.
**Pourquoi :** il n'y a rien à installer pour commencer. Le passage au serveur
ne demande que de changer une variable d'environnement.

## 2026-11-01 — Embeddings en local avec fastembed

**Décision :** les embeddings sont calculés en local avec
`paraphrase-multilingual-MiniLM-L12-v2`.
**Pourquoi :** c'est gratuit et sans clé API, le modèle est multilingue (cours
en français) et léger (~200 Mo), et fastembed est maintenu par Qdrant.
**Alternatives :** `multilingual-e5-large`, de meilleure qualité mais ~2 Go ;
une API d'embeddings payante.

## 2026-11-01 — RAG : recherche sans LLM, LLM pour la rédaction seulement

**Décision :** les sources sont les passages renvoyés par une recherche
vectorielle dans Qdrant. Le LLM ne reçoit que ces passages et rédige la réponse.
**Pourquoi :** les sources sont déterministes et vérifiables (fichier, page,
score). Le coût est réduit, puisqu'on n'envoie pas les PDF entiers au LLM.
Et on peut changer de LLM sans toucher à la recherche.
**Remplace :** la première version, qui envoyait les PDF entiers à Claude et
utilisait ses citations natives.

## 2026-11-01 — Découpage page par page

**Décision :** morceaux de 1000 caractères avec un chevauchement de 200, sans
jamais dépasser une page.
**Pourquoi :** chaque source a un numéro de page exact, pour ouvrir le PDF au
bon endroit.

## 2026-11-01 — Claude comme LLM de rédaction

**Décision :** Claude via le SDK `anthropic`, modèle configurable par
`DORA_MODEL`. Tout l'accès au LLM est isolé dans `app/llm.py`.
**Pourquoi :** bonne qualité en français. Isoler l'accès dans un fichier
permet de changer de fournisseur facilement (voir [llm.md](llm.md)).
**Historique :** cette décision a été remplacée par l'intégration Gemini, mais
elle reste conservée comme référence de la première implémentation.

## 2026-11-02 — Gemini remplace Claude comme LLM de rédaction

**Décision :** le projet utilise désormais le SDK `google-genai` pour Gemini,
avec `GEMINI_API_KEY` lu depuis `backend/.env` et le modèle défini par
`DORA_MODEL` (par défaut : `gemini-3.8-flash`). Tout l'accès au LLM reste
centralisé dans `backend/app/llm.py`.
**Pourquoi :** le fournisseur actuel est celui implémenté dans le code, avec un
accès simple via `genai.Client()` et une sortie texte brute via
`interaction.output_text`.
**Remplace :** la décision antérieure sur Claude / Anthropic, conservée ici à
titre historique.

## 2026-11-01 — Stack : FastAPI + React (Vite)

**Décision :** backend Python avec FastAPI, frontend React avec Vite, en JavaScript.
**Pourquoi :** Python est le langage de l'écosystème IA (Qdrant, embeddings,
PDF). FastAPI génère la documentation de l'API automatiquement. React permet
une vraie interface (chat, affichage des sources, quiz interactifs).
