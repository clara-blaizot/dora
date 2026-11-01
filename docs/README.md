# Documentation de Dora

Dora est une assistante de révision. On lui donne ses cours en PDF, puis on peut
lui poser des questions, générer des fiches de révision ou des quiz.

## Sommaire

| Document | Contenu |
|---|---|
| [architecture.md](architecture.md) | Vue d'ensemble : composants, dossiers, parcours d'une requête |
| [rag.md](rag.md) | Recherche des passages : découpage des PDF, embeddings, Qdrant |
| [llm.md](llm.md) | Rôle du LLM, prompts, modèles disponibles, changer de fournisseur |
| [api.md](api.md) | Routes du backend avec exemples de requêtes et réponses |
| [frontend.md](frontend.md) | Interface React : composants et appels au backend |
| [developpement.md](developpement.md) | Installation, tests, travail en branches, ajouter une fonctionnalité |
| [decisions.md](decisions.md) | Journal des choix techniques et de leurs raisons |

## État des fonctionnalités

| Fonctionnalité | État |
|---|---|
| Import de plusieurs PDF, indexation dans Qdrant | ✅ fait |
| Questions / réponses avec sources (RAG) | ✅ version de base |
| Fiches de révision | 🚧 squelette (route + écran vides) |
| Quiz | 🚧 squelette (route + écran vides) |

## Tenir la documentation à jour

Chaque Pull Request qui change un comportement met à jour la page concernée.
Si elle contient un choix technique, elle ajoute aussi une entrée dans
[decisions.md](decisions.md).
