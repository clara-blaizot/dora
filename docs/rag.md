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
| `CHUNK_SIZE` | 350 caractères | taille max d'un morceau |
| `CHUNK_OVERLAP` | 70 caractères | chevauchement entre deux morceaux consécutifs |

**Pourquoi 350 :** le modèle d'embeddings ne lit que les **128 premiers
tokens** d'un texte, et ignore le reste. Mesuré sur des cours en français :

| Texte | 400 car. | 450 car. | 500 car. |
|---|---|---|---|
| biologie (texte courant) | 108 tokens | 123 | 135 |
| maths (formules, symboles) | 154 tokens | 175 | 190 |

À 350 caractères, un texte courant tient largement dans la limite. Un texte
très dense en formules peut encore la dépasser légèrement : seuls ses derniers
mots sont alors ignorés. Le test `test_morceaux_tiennent_dans_la_fenetre_du_modele`
vérifie la limite sur un texte courant.

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
- `RAG_TOP_K` (8 par défaut) règle le nombre de passages renvoyés. Les
  morceaux étant courts, il en faut 8 pour donner assez de contexte au LLM
  (~2800 caractères au total).

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

Les limites sont classées par étape du pipeline. ⚠️ indique celles qui ont un
effet visible dès maintenant sur la qualité des réponses.

### Import et découpage des PDF

| Limite | Conséquence | Piste |
|---|---|---|
| **PDF scannés** | refusés (code 422) : pas de texte extractible | ajouter de l'OCR |
| **Tableaux, formules, images** | `pypdf` n'extrait que le texte brut : les tableaux sont aplatis, les formules souvent illisibles, les schémas perdus | extracteur plus riche (PyMuPDF, Docling…) |
| **Découpage à taille fixe** | un morceau peut couper au milieu d'une phrase ou mélanger deux sections | découper sur les phrases / titres |
| **Doublons** | importer deux fois le même PDF indexe deux fois les mêmes morceaux, et les sources apparaissent en double | refuser un PDF déjà importé (empreinte du fichier) |

### Embeddings

| Limite | Conséquence | Piste |
|---|---|---|
| **Fenêtre de 128 tokens** | ✅ corrigé en grande partie : les morceaux sont passés de 1000 à 350 caractères. Un texte très dense en formules peut encore dépasser légèrement, et la fin du morceau est alors ignorée par la recherche. Contrepartie : des morceaux courts donnent moins de contexte chacun | modèle qui lit 512 tokens (`multilingual-e5-large`, ~2 Go) ; ou chercher sur des petits morceaux mais envoyer au LLM le texte autour (« small-to-big ») |
| **Changement de modèle** | les anciens vecteurs deviennent incompatibles | réindexer : supprimer `backend/data/` et réimporter |

### Recherche

| Limite | Conséquence | Piste |
|---|---|---|
| **Pas de seuil de score** | on renvoie toujours `RAG_TOP_K` passages, même peu pertinents, et ils s'affichent comme sources | paramètre `score_threshold` de `query_points` |
| **Recherche seulement sémantique** | un mot-clé exact (nom propre, formule, sigle) peut être mal trouvé | recherche hybride (vecteurs + BM25), que Qdrant gère avec les vecteurs creux |
| **Pas de reranking** | l'ordre des résultats est approximatif | récupérer 20 passages, les reclasser avec un modèle de reranking, garder les 8 meilleurs |
| **Une seule recherche par question** | une question large (« résume le chapitre 3 ») ne trouve que `RAG_TOP_K` passages, pas tout le chapitre | pour les fiches/quiz, récupérer tous les morceaux d'un document ou faire plusieurs recherches |

### Génération de la réponse

| Limite | Conséquence | Piste |
|---|---|---|
| ⚠️ **Pas de mémoire de conversation** | chaque question est traitée seule : « et pour la page suivante ? » ou « explique plus simplement » ne fonctionnent pas. Le backend ne reçoit que la dernière question | envoyer l'historique au backend, reformuler la question en question autonome avant la recherche, puis donner l'historique au LLM |
| **Réponse vide** | ✅ corrigé : un message de repli remplace la réponse vide, et les sources restent affichées | – |
| **Citations non vérifiées** | le LLM peut citer un mauvais numéro `[n]`, ou ne rien citer | vérifier que les `[n]` de la réponse existent ; n'afficher que les sources citées |
| **Pas de streaming** | l'utilisateur attend la réponse complète sans rien voir | renvoyer la réponse au fil de l'eau (SSE) |
| **Surcharge et limites de l'offre gratuite Gemini** | ✅ en partie géré : délai max, modèle de secours, puis message clair (code 503), voir [llm.md](llm.md). Reste : quand le modèle principal ne répond pas du tout, il faut attendre `LLM_TIMEOUT` (60 s) avant le passage au secours | streaming ; délai plus court pour la première réponse |

### Stockage et fonctionnement

| Limite | Conséquence | Piste |
|---|---|---|
| **Qdrant local mono-processus** | deux backends lancés en même temps provoquent une erreur de verrou | Qdrant serveur (`docker compose up -d`) |
| **Index des documents en JSON** | pas fait pour plusieurs utilisateurs ni des écritures simultanées | base de données (SQLite) |
| **Pas de comptes utilisateurs** | tout le monde voit et cherche dans les mêmes PDF | ajouter un `user_id` dans le payload Qdrant et le filtre |
| **Historique perdu au rechargement** | la conversation n'est gardée que dans la page | la sauvegarder (navigateur ou backend) |

### Tests et fonctionnalités

| Limite | Conséquence | Piste |
|---|---|---|
| **Rédaction peu testée** | `tests/test_llm.py` teste le secours, l'erreur 503 et la réponse vide avec un Gemini simulé. Un appel réel a fonctionné le 2026-11-19, mais aucun test automatique ne vérifie la qualité des réponses | jeu de questions de référence (voir ligne suivante) |
| **Pas d'évaluation de la qualité** | impossible de mesurer si un réglage (taille des morceaux, `RAG_TOP_K`, modèle) améliore les résultats | jeu de questions avec la page attendue, et mesure du taux de bonnes sources |
| **Fiches et quiz** | n'utilisent pas encore le RAG (routes renvoyant 501) | à implémenter avec `vector_store` + `llm.py` |

## Tests

[`tests/test_rag.py`](../backend/tests/test_rag.py) teste le découpage, la
recherche et la suppression avec un Qdrant en mémoire. Aucune clé API n'est
nécessaire.
