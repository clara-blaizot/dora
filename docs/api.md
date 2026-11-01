# API du backend

URL de base : `http://localhost:8000`. Une fois le backend lancé, la
documentation interactive (Swagger) est sur http://localhost:8000/docs.

Les formats sont définis dans [`schemas.py`](../backend/app/schemas.py).

## Santé

### `GET /health`

```json
{ "status": "ok" }
```

## Documents

### `POST /documents`

Importe un ou plusieurs PDF : extraction du texte, découpage et indexation
dans Qdrant.

Requête : `multipart/form-data`, un champ `files` par PDF.

```bash
curl -F "files=@cours1.pdf" -F "files=@cours2.pdf" http://localhost:8000/documents
```

Réponse `200` :

```json
[
  { "id": "a1ccd7e4…", "filename": "cours1.pdf", "nb_pages": 12, "nb_chunks": 31 }
]
```

| Code | Cas |
|---|---|
| 400 | un fichier n'est pas un PDF |
| 422 | le PDF ne contient pas de texte (scan) |

### `GET /documents`

Liste tous les documents importés (même format que ci-dessus).

### `GET /documents/{id}/pdf`

Renvoie le PDF original. Le frontend ajoute `#page=N` pour l'ouvrir à la
bonne page. Code `404` si le document est inconnu.

### `DELETE /documents/{id}`

Supprime le PDF, ses morceaux dans Qdrant et son entrée dans l'index.
Réponse `204`, ou `404` si le document est inconnu.

## Questions / réponses

### `POST /chat`

```json
{
  "question": "Comment les plantes utilisent-elles la lumière ?",
  "document_ids": ["a1ccd7e4…"]
}
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

- `sources` vient de la recherche Qdrant (sans LLM). `answer` vient du LLM.
- `document_ids` doit contenir au moins un id. Code `404` si un id est inconnu.

## Fiches de révision (à implémenter)

### `POST /fiches`

```json
{ "document_ids": ["…"], "sujet": "chapitre 3" }
```

Réponse prévue :

```json
{ "titre": "…", "contenu_markdown": "…" }
```

Renvoie pour l'instant un code `501`.

## Quiz (à implémenter)

### `POST /quiz`

```json
{ "document_ids": ["…"], "nb_questions": 10, "sujet": null }
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
