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
| Fournisseur | Anthropic (Claude), SDK Python `anthropic` | `llm.py` |
| Modèle | `DORA_MODEL`, `claude-opus-5-5` par défaut | `.env` |
| Clé | `ANTHROPIC_API_KEY` | `.env` |
| Effort | `medium` (profondeur de réflexion du modèle) | `llm.py` |
| `max_tokens` | 16000 | `llm.py` |
| Repli | `fallbacks="default"` : si le modèle refuse une requête, l'API la rejoue sur un modèle de repli | `llm.py` |

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

## Modèles Claude disponibles

Prix en dollars par million de tokens (entrée / sortie) :

| Modèle | Identifiant | Prix | Usage conseillé |
|---|---|---|---|
| Claude Opus 5.5 | `claude-opus-5-5` | 4 $ / 20 $ | meilleure qualité de rédaction |
| Claude Sonnet 5.5 | `claude-sonnet-5-5` | 2 $ / 10 $ | bon compromis |
| Claude Haiku 5.5 | `claude-haiku-5-5` | 0,10 $ / 0,50 $ | développement, gros volumes |
| Claude Fable 5.1 | `claude-fable-5-1` | 10 $ / 50 $ | le plus puissant, surdimensionné ici |

Ordre de grandeur : une question avec 5 passages représente environ
2 000 tokens en entrée et quelques centaines en sortie.

## Autres fournisseurs possibles

| Fournisseur | Type | Remarque |
|---|---|---|
| OpenAI (GPT) | API payante | même principe |
| Google (Gemini) | API payante | même principe |
| Mistral | API payante + modèles open source | entreprise française |
| Ollama (Llama, Mistral, Qwen…) | local, gratuit | demande une machine puissante, qualité moindre |

Pour en ajouter un, il faut réécrire `create_message` dans `llm.py` et adapter
la lecture de la réponse dans les services. Pour l'instant, ils lisent
`response.content` et `response.stop_reason` au format Anthropic.
