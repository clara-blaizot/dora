# API du backend

URL de base : `http://localhost:8000`. Une fois le backend lancé, la
documentation interactive (Swagger) est sur http://localhost:8000/docs.

Les formats sont définis dans [`schemas.py`](../backend/app/schemas.py).

**Principe :** tout est organisé par **matière**. Chaque PDF appartient à une
seule matière, et les questions, fiches et quiz portent sur une matière : Dora
n'utilise alors que les PDF de cette matière.

| Méthode | Route | Rôle |
|---|---|---|
| `GET` | `/health` | le backend répond |
| `GET` | `/subjects` | lister les matières |
| `POST` | `/subjects` | créer une matière |
| `PATCH` | `/subjects/{id}` | renommer / changer la couleur |
| `DELETE` | `/subjects/{id}` | supprimer une matière **et ses PDF** |
| `GET` | `/subjects/{id}/documents` | PDF d'une matière |
| `POST` | `/subjects/{id}/documents` | importer des PDF dans une matière |
| `POST` | `/subjects/{id}/ask` | poser une question sur les cours de la matière |
| `POST` | `/subjects/{id}/fiches` | 🚧 fiche de révision (501) |
| `POST` | `/subjects/{id}/quiz` | 🚧 quiz (501) |
| `GET` | `/documents` | tous les PDF, toutes matières confondues |
| `GET` | `/documents/{id}/pdf` | PDF original |
| `DELETE` | `/documents/{id}` | supprimer un PDF |

Toute route `/subjects/{id}/…` renvoie `404` (« Matière inconnue ») si la
matière n'existe pas.

## Santé

### `GET /health`

```json
{ "status": "ok" }
```

## Matières

### `GET /subjects`

```json
[
  { "id": "725d2c0d…", "name": "Physique", "color": "#F783AC" }
]
```

### `POST /subjects`

```json
{ "name": "Physique", "color": "#F783AC" }
```

- `name` : de 1 à 80 caractères.
- `color` : optionnelle, au format `#RRGGBB` (par défaut `#D6336C`).

Réponse `201` : la matière créée. Code `422` si le nom est vide ou la couleur invalide.

### `PATCH /subjects/{id}`

On envoie seulement les champs à modifier :

```json
{ "name": "Physique quantique" }
```

Réponse `200` : la matière modifiée.

### `DELETE /subjects/{id}`

Supprime la matière **et tous ses PDF** (fichiers, morceaux dans Qdrant,
index). Réponse `204`.

## Documents

### `POST /subjects/{id}/documents`

Importe un ou plusieurs PDF dans la matière : extraction du texte, découpage,
puis indexation dans Qdrant avec le `subject_id`.

Requête : `multipart/form-data`, un champ `files` par PDF.

```bash
curl -F "files=@cours1.pdf" -F "files=@cours2.pdf" http://localhost:8000/subjects/<id>/documents
```

Réponse `200` :

```json
[
  { "id": "a1ccd7e4…", "subject_id": "725d2c0d…", "filename": "cours1.pdf", "nb_pages": 12, "nb_chunks": 31 }
]
```

| Code | Cas |
|---|---|
| 400 | un fichier n'est pas un PDF |
| 404 | matière inconnue |
| 422 | le PDF ne contient pas de texte (scan) |

### `GET /subjects/{id}/documents` et `GET /documents`

Ces routes listent les PDF d'une matière, ou tous les PDF (même format que
ci-dessus). Le frontend utilise `GET /documents` puis filtre sur `subject_id`.

### `GET /documents/{id}/pdf`

Renvoie le PDF original. Le frontend ajoute `#page=N` pour l'ouvrir à la
bonne page. Code `404` si le document est inconnu.

### `DELETE /documents/{id}`

Supprime le PDF, ses morceaux dans Qdrant et son entrée dans l'index.
Réponse `204`, ou `404` si le document est inconnu.

## Questions / réponses

### `POST /subjects/{id}/ask`

```json
{ "question": "Comment les plantes utilisent-elles la lumière ?" }
```

Réponse `200` :

```json
{
  "answer": "Grâce à la photosynthèse, qui transforme la lumière en énergie chimique [1].",
  "sources": [
    {
      "numero": 1,
      "document_id": "a1ccd7e4…",
      "filename": "cours1.pdf",
      "page": 2,
      "text": "La photosynthèse transforme la lumière en énergie chimique.",
      "score": 0.44
    }
  ]
}
```

- La recherche ne porte **que sur les PDF de la matière** (filtre `subject_id`
  dans Qdrant). Une question de maths posée dans « Physique » ne renverra que
  des passages de physique.
- `sources` vient de la recherche Qdrant (sans LLM). `answer` vient du LLM.
- Si la matière n'a aucun PDF, `sources` est vide et `answer` le signale.
- Code `422` si `question` est vide.
- Code `503` si le LLM est indisponible (modèle principal et modèle de secours
  surchargés, quota atteint ou réseau). `detail` contient un message en
  français à afficher tel quel.
- Si le LLM renvoie une réponse vide, `answer` contient un message de repli et
  `sources` reste rempli.

## Fiches de révision (à implémenter)

### `POST /subjects/{id}/fiches`

```json
{ "sujet": "chapitre 3" }
```

`sujet` est optionnel. Sans lui, la fiche porte sur toute la matière.
Réponse prévue :

```json
{ "titre": "…", "contenu_markdown": "…" }
```

Renvoie pour l'instant un code `501`.

## Quiz (à implémenter)

### `POST /subjects/{id}/quiz`

```json
{ "nb_questions": 10, "sujet": null }
```

`nb_questions` doit être entre 1 et 50. Réponse prévue :

```json
{
  "titre": "…",
  "questions": [
    {
      "question": "…",
      "choix": ["A", "B", "C", "D"],
      "bonne_reponse": 2,
      "explication": "…"
    }
  ]
}
```

Renvoie pour l'instant un code `501`.
