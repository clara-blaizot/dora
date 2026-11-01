# Frontend

React 18 + Vite, en JavaScript, sans bibliothèque de composants ni de routing.
Code : [`frontend/src/`](../frontend/src/)

## Configuration

`VITE_API_URL` (fichier `frontend/.env`, voir `.env.example`) donne l'adresse
du backend. Par défaut : `http://localhost:8000`.

## Structure

```
src/
├── main.jsx              point d'entrée React
├── App.jsx               barre latérale (documents) + onglets (Questions, Fiches, Quiz)
├── api.js                une fonction par route du backend
├── styles.css            styles globaux (variables CSS dans :root)
└── components/
    ├── DocumentsPanel.jsx   import, sélection (cases à cocher), suppression des PDF
    ├── Chat.jsx             conversation : question → réponse + sources
    ├── Sources.jsx          liste dépliable des passages [n] avec lien vers la page du PDF
    ├── Fiches.jsx           🚧 à implémenter
    └── Quiz.jsx             🚧 à implémenter
```

## État

L'état est entièrement dans `App.jsx`, sans Redux ni Context :

| État | Rôle |
|---|---|
| `documents` | liste renvoyée par `GET /documents` |
| `selectedIds` | PDF cochés, transmis à chaque onglet en prop `documentIds` |
| `tab` | onglet actif |

L'historique de conversation est local au composant `Chat`. Il est perdu au
rechargement de la page.

## Ajouter un onglet

1. Créer `components/MonOnglet.jsx`, qui reçoit `{ documentIds }`.
2. L'ajouter dans l'objet `TABS` de `App.jsx`.
3. Ajouter la fonction d'appel au backend dans `api.js`.
