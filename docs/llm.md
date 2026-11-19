# LLM

## Rôle

Le LLM ne fait **que rédiger**. Il ne cherche rien. Il reçoit les passages déjà
trouvés par le [RAG](rag.md) et s'en sert pour :

- répondre à une question (fait),
- produire une fiche de révision (à faire),
- produire un quiz (à faire).

Tout appel au LLM passe par [`backend/app/llm.py`](../backend/app/llm.py).
Pour changer de modèle ou de fournisseur, on ne modifie que ce fichier.

## Configuration actuelle

| Réglage | Valeur | Où |
|---|---|---|
| Fournisseur | Gemini via le SDK Python `google-genai` | `backend/app/llm.py` |
| Modèle | `DORA_MODEL`, valeur par défaut `gemini-3.8-flash` | `backend/app/config.py` |
| Modèle de secours | `DORA_FALLBACK_MODEL`, valeur par défaut `gemini-3.1-flash-lite` (vide = désactivé) | `backend/app/config.py` |
| Délai max | `LLM_TIMEOUT`, 60 secondes par tentative | `backend/app/config.py` |
| Essais | 2 par modèle (`HttpRetryOptions(attempts=2)`) | `backend/app/llm.py` |
| Clé | `GEMINI_API_KEY` | `backend/.env` |
| Client | `genai.Client()` ; le SDK lit automatiquement la clé depuis les variables d'environnement | `backend/app/llm.py` |
| `max_tokens` | 16000 | `backend/app/llm.py` |
| Réponse | `interaction.output_text` renvoyée sous forme de texte brut | `backend/app/llm.py` |

Le client est initialisé dans `get_client()`, et `create_message()` compose un
prompt unique à partir des messages, l'envoie au modèle, puis renvoie
`interaction.output_text` sans transformation supplémentaire.

## Modèle surchargé, quota, réseau

Les modèles Gemini, surtout avec l'offre gratuite, sont souvent **surchargés**.
L'API répond alors par une erreur 503 (« experiencing high demand »), ou ne
répond pas du tout. Sans réglage, le SDK réessaie en boucle **sans rien
afficher**, et l'appel semble bloqué indéfiniment.

Ce que fait `create_message()` :

1. Il essaie `DORA_MODEL`, 2 fois au maximum, avec un délai de `LLM_TIMEOUT` secondes.
2. En cas d'erreur passagère (429 quota, 5xx surcharge, délai dépassé, réseau),
   il passe à `DORA_FALLBACK_MODEL`. Ces erreurs sont listées dans `ERREURS_TEMPORAIRES`.
3. Si le secours échoue aussi, il lève `LLMIndisponible`. La route `/subjects/{id}/ask` la
   transforme en **code 503** avec un message en français, que le frontend
   affiche dans la bulle de Dora.

Les autres erreurs (clé invalide, modèle inexistant…) ne déclenchent pas le
secours : ce sont des erreurs de configuration, à corriger dans `.env`.

Si Gemini renvoie une réponse **vide** (réponse bloquée par exemple),
`services/chat.py` la remplace par un message invitant à reformuler. Les
sources restent affichées.

**Constaté le 2026-11-19 :** `gemini-3.8-flash`, `3.7-flash`, `3.6-flash` et
`3.5-flash` étaient surchargés, tandis que `gemini-3.1-flash-lite` et
`3.5-flash-lite` répondaient en quelques secondes. Si la surcharge dure, mettez
`DORA_MODEL=gemini-3.1-flash-lite` dans votre `.env` pour éviter d'attendre
le délai à chaque question.

**Tester sa clé et le modèle** (depuis `backend/`) :

```bash
.venv/bin/python -c "from app.llm import create_message; print(create_message(system='Réponds en une phrase.', messages=[{'role': 'user', 'content': 'Dis bonjour.'}]))"
```

Pour lister les modèles accessibles avec votre clé :

```bash
.venv/bin/python -c "from app.llm import get_client; print([m.name for m in get_client().models.list()])"
```

## Prompt des questions / réponses

Défini dans [`services/chat.py`](../backend/app/services/chat.py).

**Système :** Dora répond en français, de façon pédagogique, en s'appuyant
**uniquement** sur les extraits fournis. Elle cite les extraits avec `[n]` et
dit quand les extraits ne permettent pas de répondre.

**Message utilisateur :**

```
<extraits>
[1] (cours.pdf, page 2)
La photosynthèse transforme…

[2] (cours.pdf, page 5)
…
</extraits>

Question : comment les plantes utilisent-elles la lumière ?
```

Les numéros `[n]` correspondent aux `numero` des sources renvoyées au frontend.

## Modèles Gemini disponibles

La variable `DORA_MODEL` permet de choisir le modèle Gemini utilisé par le
backend. Par défaut, le projet cible `gemini-3.8-flash`.

**Pourquoi Gemini :** l'API propose une offre gratuite (avec des limites de
requêtes), ce qui permet de développer et tester Dora sans frais. Les détails
sont dans [decisions.md](decisions.md).

Exemples de modèles Gemini courants :

| Modèle | Identifiant | Usage conseillé |
|---|---|---|
| Gemini 3.8 Flash | `gemini-3.8-flash` | bon compromis pour la rédaction de réponses |
| Gemini 3.8 Pro | `gemini-3.8-pro` | meilleure qualité, plus coûteux |
| Gemini 2.5 Flash | `gemini-2.5-flash` | alternative légère et rapide |

Ordre de grandeur : une question avec 8 passages de 350 caractères représente
environ 1 000 à 1 500 tokens en entrée et quelques centaines en sortie.

## Autres fournisseurs possibles

| Fournisseur | Type | Remarque |
|---|---|---|
| OpenAI (GPT) | API payante | même principe |
| Google (Gemini) | API payante | fournisseur actuel |
| Mistral | API payante + modèles open source | entreprise française |
| Ollama (Llama, Mistral, Qwen…) | local, gratuit | demande une machine puissante, qualité moindre |

Pour en ajouter un, il faut réécrire `create_message` dans `llm.py` et adapter
la lecture de la réponse dans les services. Le code actuel lit directement
`interaction.output_text` et le renvoie comme texte brut.
