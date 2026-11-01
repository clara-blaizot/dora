# RAG : recherche des passages

RAG veut dire *Retrieval-Augmented Generation* : on **retrouve** d'abord les
passages utiles, puis on **génère** la réponse à partir d'eux. Dans Dora,
l'étape de recherche n'utilise aucun LLM. Elle se fait entièrement par
similarité de vecteurs dans Qdrant.

Code : [`backend/app/rag/`](../backend/app/rag/)

## 1. Import d'un PDF (indexation)

```
PDF ──► extract_pages ──► chunk_pages ──► embed ──► Qdrant.upsert
        (pypdf)           (morceaux)      (vecteurs)
```

### Extraction : `pdf.extract_pages`

- `pypdf` extrait le texte de chaque page.
- Les espaces et retours à la ligne multiples sont réduits à un seul espace.
- Une page sans texte donne une chaîne vide. Si le PDF entier est vide (scan
  sans OCR), l'import est refusé avec un code 422.

### Découpage : `pdf.chunk_pages`

| Paramètre | Valeur | Rôle |
|---|---|---|
| `CHUNK_SIZE` | 1000 caractères | taille max d'un morceau |
| `CHUNK_OVERLAP` | 200 caractères | chevauchement entre deux morceaux consécutifs |

- Le découpage se fait **page par page**. Un morceau n'est donc jamais à
  cheval sur deux pages, ce qui permet de renvoyer un numéro de page exact.
- La coupe se fait sur un espace, pour ne pas couper un mot en deux.
- Le chevauchement évite qu'une idée coupée entre deux morceaux soit perdue.

**Réglage :** des morceaux plus petits donnent des sources plus précises mais
avec moins de contexte. Des morceaux plus grands donnent l'inverse.

### Embeddings : `embeddings.embed`

- Bibliothèque : [fastembed](https://github.com/qdrant/fastembed). Les calculs
  se font en local, sans API et gratuitement.
- Modèle par défaut : `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
  (multilingue, donc bon en français, vecteurs de 384 dimensions, ~200 Mo).
  Il se télécharge au premier usage.
- Variable : `EMBEDDING_MODEL`. Les autres modèles multilingues disponibles
  sont `paraphrase-multilingual-mpnet-base-v2`, `intfloat/multilingual-e5-large`
  (meilleur mais ~2 Go) et `minishlab/potion-multilingual-128M`.

> ⚠️ Changer de modèle change la dimension des vecteurs. Il faut alors
> supprimer `backend/data/` (ou la collection Qdrant) et réimporter les PDF.

### Stockage : `vector_store.index_chunks`

Chaque morceau devient un point Qdrant :

```json
{
  "id": "uuid aléatoire",
  "vector": [0.012, -0.08, ...],
  "payload": {
    "document_id": "a1cc…",
    "filename": "cours.pdf",
    "page": 2,
    "text": "La photosynthèse transforme…"
  }
}
```

Collection : `QDRANT_COLLECTION` (`cours` par défaut), distance **cosinus**.
Elle est créée automatiquement au premier accès.

## 2. Recherche : `vector_store.search`

```
question ──► embed ──► Qdrant.query_points(filtre document_id ∈ PDF cochés, limit=RAG_TOP_K)
```

- Seuls les PDF sélectionnés dans l'interface sont cherchés (filtre `MatchAny`).
- Le résultat est une liste de `SearchResult(document_id, filename, page, text, score)`.
- `score` est la similarité cosinus : plus elle est haute, plus le passage est proche.
- `RAG_TOP_K` (5 par défaut) règle le nombre de passages renvoyés.

## 3. Suppression : `vector_store.delete_document`

Elle supprime tous les points dont `document_id` correspond.

## Qdrant : local ou serveur

| Mode | Configuration | Usage |
|---|---|---|
| Local (par défaut) | `QDRANT_URL` vide → fichiers dans `backend/data/qdrant` | développement, rien à installer |
| Serveur | `docker compose up -d` + `QDRANT_URL=http://localhost:6333` | tableau de bord, index de payload, plusieurs processus |

En mode local, **un seul processus** peut ouvrir la base à la fois. Lancer
deux backends en même temps provoque une erreur de verrou.

## Limites connues et pistes

- **PDF scannés** : refusés pour l'instant. Piste : ajouter de l'OCR.
- **Recherche seulement sémantique** : un mot-clé exact (nom propre, formule)
  peut être mal trouvé. Piste : recherche hybride (vecteurs + BM25), que Qdrant
  gère avec les vecteurs creux.
- **Pas de reranking** : piste, reclasser les 20 premiers résultats avec un
  modèle de reranking avant d'en garder 5.
- **Pas de seuil de score** : on renvoie toujours `RAG_TOP_K` passages, même
  peu pertinents. Piste : le paramètre `score_threshold` de `query_points`.

## Tests

[`tests/test_rag.py`](../backend/tests/test_rag.py) teste le découpage, la
recherche et la suppression avec un Qdrant en mémoire. Aucune clé API n'est
nécessaire.
