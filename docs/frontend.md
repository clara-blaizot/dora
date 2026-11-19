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
| `subjects` | `useSubjects` | `[{id, name, color}]`, chargées par `GET /subjects` | backend |
| `status` | `useSubjects` | `loading` / `ready` / `error` (backend injoignable) | non |
| `activeId` | `App` | matière affichée (la première par défaut) | non |
| `documents` | `App` | tous les PDF (`GET /documents`), filtrés par `subject_id` pour l'affichage | backend |
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

`Source` est l'objet renvoyé par `POST /subjects/{id}/ask` : `{numero,
document_id, filename, page, text, score}` (voir [api.md](api.md)).
`error: true` affiche la bulle en orange (backend injoignable, LLM surchargé…).

## Matières

Les matières sont stockées dans le **backend** (voir [api.md](api.md)) :

- Au chargement, `useSubjects` appelle `GET /subjects`. Si la liste est vide
  (premier lancement), il crée « Ma matière ». Le chargement est partagé pour
  ne pas créer deux matières à cause du double appel des effets de React en
  développement (`StrictMode`).
- « Nouvelle matière » appelle `POST /subjects`, avec une couleur prise dans
  une palette.
- Un PDF est importé **dans** la matière active (`POST /subjects/{id}/documents`).
- Une question est posée **à** la matière active (`POST /subjects/{id}/ask`).
  C'est le backend qui garantit que seuls ses PDF sont utilisés.
- Si le backend est injoignable au chargement, l'écran affiche un message à la
  place de l'application.

Pas encore dans l'interface (mais déjà dans l'API) : renommer, recolorer ou
supprimer une matière (`PATCH` / `DELETE /subjects/{id}`).

## Ajouter une fonctionnalité (ex. brancher Fiche ou Quiz)

1. Utiliser la fonction d'appel dans `api.js` (`createFiche(subjectId, sujet)`
   et `createQuiz(subjectId, nbQuestions, sujet)` existent déjà).
2. Dans `ChatPanel.jsx`, retirer `disabled` et le badge « bientôt » du bouton.
   Ajouter un `onClick` remonté à `App.jsx`.
3. Dans `App.jsx`, appeler l'API avec `subject.id` et afficher le résultat
   (nouveau composant dans `components/`).
4. Mettre à jour cette page.
