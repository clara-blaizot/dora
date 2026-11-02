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
| Clé | `GEMINI_API_KEY` | `backend/.env` |
| Client | `genai.Client()` ; le SDK lit automatiquement la clé depuis les variables d'environnement | `backend/app/llm.py` |
| `max_tokens` | 16000 | `backend/app/llm.py` |
| Réponse | `interaction.output_text` renvoyée sous forme de texte brut | `backend/app/llm.py` |

Le client est initialisé dans `get_client()`, et `create_message()` compose un
prompt unique à partir des messages, envoie la requête au modèle courant, puis
renvoie `interaction.output_text` sans transformation supplémentaire.

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

Exemples de modèles Gemini courants :

| Modèle | Identifiant | Usage conseillé |
|---|---|---|
| Gemini 3.8 Flash | `gemini-3.8-flash` | bon compromis pour la rédaction de réponses |
| Gemini 3.8 Pro | `gemini-3.8-pro` | meilleure qualité, plus coûteux |
| Gemini 2.5 Flash | `gemini-2.5-flash` | alternative légère et rapide |

Ordre de grandeur : une question avec 5 passages représente environ
2 000 tokens en entrée et quelques centaines en sortie.

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
