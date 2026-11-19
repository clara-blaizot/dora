# Journal des décisions

Chaque choix technique important, avec sa raison. Les entrées les plus
récentes sont en haut. Pour revenir sur une décision, ajoutez une nouvelle
entrée plutôt que d'effacer l'ancienne.

---

## 2026-11-19 — Nouveau frontend d'après la maquette, matières côté navigateur

**Décision :** le frontend est réécrit en React d'après `dora-maquette.html` :
matières dans la barre latérale, chat au centre, volet Sources ouvert par les
citations, barre « Mes cours ». Les matières (et la liste des PDF de chacune)
sont gérées dans le navigateur (`localStorage`), le backend n'est pas modifié.
Fiche et Quiz sont affichés mais désactivés (« bientôt »).
**Pourquoi :** la maquette organise les cours par matière, ce que le backend
ne gère pas encore. Les gérer côté navigateur permet d'avancer le frontend
sans toucher au backend, puisque `/chat` accepte déjà une liste de
`document_ids`.
**Conséquences :** les matières ne sont pas partagées entre navigateurs. Les
PDF sans matière sont rangés dans la première matière. Voir
[frontend.md](frontend.md).
**Écarté pour l'instant :** TypeScript (suggéré par la maquette). On reste en
JavaScript, comme le reste du frontend.

## 2026-11-19 — Modèle de secours et délai max pour Gemini

**Décision :** chaque appel au LLM a un délai max (`LLM_TIMEOUT`, 60 s) et au
plus 2 essais. En cas de surcharge, de quota atteint ou de problème réseau, on
passe à `DORA_FALLBACK_MODEL` (`gemini-3.1-flash-lite`). Si lui aussi échoue,
`/chat` renvoie une erreur 503 avec un message clair.
**Pourquoi :** au premier essai réel, la commande de test semblait « ne rien
faire ». En réalité, `gemini-3.8-flash` était surchargé (503 « high demand »)
ou ne répondait pas, et le SDK réessayait en boucle, sans limite et sans rien
afficher. Les modèles Flash-Lite, eux, répondaient en quelques secondes.
**Alternatives :** passer directement à Flash-Lite par défaut. Écarté pour
l'instant, car la surcharge de Flash est sans doute passagère et Flash donne
de meilleures réponses. Chacune peut changer `DORA_MODEL` dans son `.env`.

## 2026-11-19 — Morceaux de 350 caractères, 8 passages par question

**Décision :** `CHUNK_SIZE` passe de 1000 à 350 caractères (chevauchement de
200 à 70), et `RAG_TOP_K` de 5 à 8.
**Pourquoi :** le modèle d'embeddings ne lit que les 128 premiers tokens d'un
texte. Avec 1000 caractères, environ la moitié de chaque morceau était ignorée
par la recherche. Mesures sur des cours en français : 128 tokens ≈ 470
caractères de texte courant, mais seulement ≈ 330 caractères de texte dense en
formules. 350 est un compromis. Comme chaque morceau est plus court, on en
renvoie 8 au lieu de 5 pour garder assez de contexte au LLM.
**Conséquences :** les PDF importés avant ce changement doivent être
réimportés (supprimer `backend/data/` puis réimporter).
**Alternatives écartées pour l'instant :** `multilingual-e5-large` (lit 512
tokens mais pèse ~2 Go) ; la technique « small-to-big » (plus complexe).

## 2026-11-02 — Gemini remplace Claude comme LLM de rédaction

**Décision :** le projet utilise désormais Gemini via le SDK `google-genai`,
avec `GEMINI_API_KEY` lu depuis `backend/.env` et le modèle défini par
`DORA_MODEL` (par défaut : `gemini-3.8-flash`). Tout l'accès au LLM reste
centralisé dans `backend/app/llm.py`.
**Pourquoi :** l'API Gemini propose une offre **gratuite** (avec des limites
de requêtes), alors que l'API Claude est payante dès le premier appel. Pour un
projet étudiant sans budget, on peut ainsi développer et tester sans frais.
Comme le LLM ne fait que rédiger à partir des passages trouvés par le RAG, un
modèle « Flash » suffit.
**Conséquences :** il faut surveiller les limites de l'offre gratuite. Si elles
deviennent bloquantes, ou si la qualité ne suffit pas, il suffira de changer
`llm.py` (voir [llm.md](llm.md)).
**Remplace :** la décision « Claude comme LLM de rédaction » du 2026-11-01,
conservée plus bas à titre historique.

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
jamais dépasser une page. (Taille réduite à 350 le 2026-11-19, voir plus haut.)
**Pourquoi :** chaque source a un numéro de page exact, pour ouvrir le PDF au
bon endroit.

## 2026-11-01 — Claude comme LLM de rédaction

**Décision :** Claude via le SDK `anthropic`, modèle configurable par
`DORA_MODEL`. Tout l'accès au LLM est isolé dans `app/llm.py`.
**Pourquoi :** bonne qualité en français. Isoler l'accès dans un fichier
permet de changer de fournisseur facilement (voir [llm.md](llm.md)).
**Historique :** remplacée le 2026-11-02 par Gemini (voir l'entrée en haut).

## 2026-11-01 — Stack : FastAPI + React (Vite)

**Décision :** backend Python avec FastAPI, frontend React avec Vite, en JavaScript.
**Pourquoi :** Python est le langage de l'écosystème IA (Qdrant, embeddings,
PDF). FastAPI génère la documentation de l'API automatiquement. React permet
une vraie interface (chat, affichage des sources, quiz interactifs).
