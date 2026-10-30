# `agents/` — Orchestration agentique LangGraph

**Casquette** : Agents & sécurité · **Étape** : 7

## Contrat d'interface

| Entrée | Sortie |
|---|---|
| `Alert` normalisée (`data/schemas.py`) | `InvestigationResult` : priorité, explication, score de risque, action proposée |
| LLM servi (étape 6), `rag.retrieve()`, `kg` | trajectoire complète tracée (LLMOps, étape 10) |

## État partagé (`SOCState`)

Champs minimaux imposés par la feuille de route :

```python
class SOCState(TypedDict):
    alert: Alert
    priority: Literal["low", "medium", "high", "critical"]
    rag_context: Context | None
    graph_context: dict | None
    threat_intel: dict | None
    risk_score: float | None
    proposed_actions: list[ActionProposal]
    history: list[Step]          # trace ordonnée des décisions
    iterations: int              # garde-fou anti-boucle
```

## Agents

| Agent | Responsabilité | Ne fait pas |
|---|---|---|
| Triage | priorité, décision d'arrêt si priorité basse | pas d'investigation |
| Investigation | orchestrateur : appelle les autres, agrège | pas d'appel direct au LLM sans contexte |
| RAG | interroge `rag.retrieve()` | pas d'action |
| Knowledge Graph | interroge Neo4j, sérialise le sous-graphe | pas de génération libre |
| Threat Intelligence | enrichit (KEV, CTI) | pas de verdict final |
| Response | propose une action structurée | **n'exécute rien** |

## Exigences techniques

1. **Transitions conditionnelles** : priorité basse → `END` ; sinon enquête complète.
2. **Checkpointer** obligatoire : l'état doit survivre à une reprise de session.
3. **Human-in-the-loop** : `interrupt_before=["response"]` — l'agent Response ne
   produit une action qu'après décision humaine ; l'exécution reste dans
   `security/` (étape 8).
4. **Gestion d'erreurs** : timeout par nœud, JSON invalide → réessai borné,
   `iterations` maximum pour éviter les boucles infinies.
5. **Version mono-agent** obligatoire : un seul prompt avec tous les outils,
   pour la comparaison Single vs Multi-Agent de l'étape 12.

## Arborescence

```
agents/
├── state.py        # SOCState, schémas d'étapes
├── graph.py        # construction du StateGraph + checkpointer
├── nodes/          # un fichier par agent
├── single_agent.py # baseline mono-agent (comparaison finale)
└── prompts/        # prompts versionnés (v1, v2…) — diffusés dans Git
```

## Critère de réussite de l'étape 7

Une alerte du jeu de test traverse tout le graphe et produit une **action
structurée valide** (validée par le schéma de `security/actions.py`).

## Règle d'or

Aucun nœud du graphe n'a d'effet de bord sur le système réel : les agents
*proposent*, le module `security/` *valide*, l'humain *approuve*, la sandbox *simule*.
