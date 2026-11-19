# Frontend

React 18 + Vite, en JavaScript, sans bibliothèque de composants ni de routing.
Code : [`frontend/src/`](../frontend/src/)

Le design suit la maquette [`dora-maquette.html`](../dora-maquette.html) (à
ouvrir dans un navigateur) : thème rose, police Plus Jakarta Sans, chat au
centre, volet Sources à droite, barre « Mes cours » en bas.

## Configuration

`VITE_API_URL` (fichier `frontend/.env`, voir `.env.example`) donne l'adresse
du backend. Par défaut : `http://localhost:8000`.

## Écran

```
┌────────────┬──────────────────────────────────────────────────────────┐
│ Dora       │ <Nom de la matière>                                      │
│            │ ┌──────────────────────────────┐ ┌──────────────────────┐│
│ MES        │ │ Demande à Dora  [Fiche][Quiz]│ │ Sources   8 passages ││
│ MATIÈRES   │ │                              │ │ [1] cours.pdf  p.3 ↗ ││
│ ● Analyse  │ │  question ►                  │ │ « passage… »         ││
│ ● Physique │ │  ◄ réponse [1] [2] [3]       │ │ [2] …                ││
│ + Nouvelle │ │ [ Pose ta question…    ] [→] │ │                      ││
│            │ └──────────────────────────────┘ └──────────────────────┘│
│            │ Mes cours : (PDF cours.pdf ×) (+ Ajouter)                │
└────────────┴──────────────────────────────────────────────────────────┘
```

- **Matières** (barre de gauche) : chaque matière a ses propres PDF et sa
  propre conversation. « Nouvelle matière » ouvre un champ pour saisir le nom.
- **Chat** : Entrée ou la flèche envoie la question. Dora interroge
  uniquement les PDF de la matière active.
- **Citations** : sous chaque réponse, les boutons `[n] fichier · p. X`
  ouvrent le volet Sources sur le passage correspondant.
- **Volet Sources** : apparaît seulement quand une réponse contient des
  sources. Le lien `p. X ↗` ouvre le PDF à la bonne page.
- **Mes cours** : import (multi-PDF) et suppression des PDF de la matière.
  Une suppression demande confirmation et efface le PDF du backend.
- **Fiche / Quiz** : boutons désactivés avec la mention « bientôt », en
  attendant que le backend les implémente (routes `/fiches` et `/quiz` en 501).

## Structure

```
src/
├── main.jsx                  point d'entrée React
├── App.jsx                   état global, appels au backend, mise en page
├── api.js                    une fonction par route du backend
├── styles.css                thème de la maquette (variables CSS dans :root)
├── hooks/
│   └── useSubjects.js        matières + PDF de chaque matière (sauvegardés dans le navigateur)
└── components/
    ├── Sidebar.jsx           liste des matières, création d'une matière
    ├── ChatPanel.jsx         en-tête (Fiche/Quiz désactivés), messages, citations, saisie
    ├── SourcesPanel.jsx      volet des passages [n], lien vers la page du PDF
    ├── CoursesBar.jsx        PDF de la matière : import, suppression
    └── icons.jsx             icônes SVG de la maquette
```

## État

| État | Où | Rôle | Persistance |
|---|---|---|---|
| `subjects` | `useSubjects` | `[{id, name, color, docIds}]` | `localStorage` (`dora.subjects`) |
| `activeId` | `App` | matière affichée | non |
| `documents` | `App` | tous les PDF renvoyés par `GET /documents` | backend |
| `conversations` | `App` | `{[subjectId]: {messages, panel}}` | non, perdu au rechargement |
| `thinkingId` | `App` | matière qui attend une réponse (« Dora réfléchit… ») | non |
| `notice` | `App` | message d'erreur (import, backend injoignable) | non |

`panel = {open, messageId, activeN}` indique quel message alimente le volet
Sources et quel passage est en surbrillance.

Si on change de matière pendant que Dora répond, la réponse s'ajoute bien à la
matière d'origine.

### Messages

```js
{ id, role: "user", text }
{ id, role: "dora", text, sources?: Source[], error?: true }
```

`Source` est l'objet renvoyé par `POST /chat` : `{numero, document_id,
filename, page, text, score}` (voir [api.md](api.md)). `error: true` affiche la
bulle en orange (backend injoignable, LLM surchargé…).

## Matières : gérées côté navigateur

Le backend ne connaît pas les matières : il ne connaît que des PDF. Le
frontend associe donc chaque PDF à une matière et envoie à `POST /chat` les
`document_ids` de la matière active.

Conséquences :

- Les matières sont propres à chaque navigateur. Un autre navigateur ou
  ordinateur ne les voit pas.
- Un PDF présent dans le backend mais rangé dans aucune matière (importé
  avant cette version, ou depuis un autre navigateur) est rangé
  automatiquement dans la **première matière**.
- On ne peut pas encore renommer, supprimer ou recolorer une matière.

Piste : ajouter les matières au backend (`/subjects`, avec un `subject_id`
dans le payload Qdrant). Le hook `useSubjects` serait alors remplacé par des
appels à l'API.

## Ajouter une fonctionnalité (ex. brancher Fiche ou Quiz)

1. Ajouter ou utiliser la fonction d'appel dans `api.js` (`createFiche` et
   `createQuiz` existent déjà).
2. Dans `ChatPanel.jsx`, retirer `disabled` et le badge « bientôt » du bouton.
   Ajouter un `onClick` remonté à `App.jsx`.
3. Dans `App.jsx`, appeler l'API avec `docs.map((d) => d.id)` et afficher le
   résultat (nouveau composant dans `components/`).
4. Mettre à jour cette page.
