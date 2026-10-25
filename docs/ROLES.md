# Répartition des rôles — CyberSOC AI

> **Statut : à valider en réunion de lancement (semaine 1).**
> Les colonnes « Membre » contiennent des placeholders `M1` … `M5` : chaque
> personne écrit son prénom puis signe la ligne. Tant que ce fichier n'est pas
> rempli, la règle « une PR relue par un autre membre » reste inapplicable.

## 1. Les cinq rôles et le rôle transverse

| # | Rôle | Membre | Périmètre | Étapes portées |
|---|------|--------|-----------|----------------|
| 1 | **Données & RAG** | `M1` | Collecte MITRE/KEV/CWE, normalisation JSONL, chunking, embeddings, Vector-RAG, listes d'IDs valides, datasheet | 1, 3 |
| 2 | **Knowledge Graph** | `M2` | Schéma Neo4j, import, requêtes Cypher, Graph-RAG, Hybrid RAG, fusion RRF | 4 |
| 3 | **Modèles & optimisation** | `M3` | Benchmark SLM, fine-tuning LoRA/QLoRA, quantification FP16/INT8/INT4, vLLM, KV cache, mesures de performance | 2, 5, 6 |
| 4 | **Agents & sécurité** | `M4` | LangGraph, sandbox d'actions, jeu d'attaques et défenses LLM, scénarios synthétiques | 7, 8, 9 |
| 5 | **Web & LLMOps** | `M5` | FastAPI, React/TypeScript, MLflow/Langfuse, journal d'audit, intégration continue, démo | 10, 11 |
| + | **Responsable d'intégration** | **à désigner** (recommandé : `M5`) | Point de passage unique pour `main`, arbitrage des interfaces entre modules, garde du calendrier, propriétaire du README | toutes |

Le responsable d'intégration n'est pas un sixième membre : c'est une casquette
supplémentaire. Son intérêt est d'éviter le risque n°1 du projet (« intégrer
trop tard ») : c'est lui qui impose un pipeline minimal de bout en bout dès la
semaine 4, même dégradé.

## 2. Matrice RACI par étape

`R` = réalise · `A` = approuve (responsable final) · `C` = consulté · `I` = informé

| Étape | M1 Données/RAG | M2 KG | M3 Modèles | M4 Agents/Sécu | M5 Web/LLMOps | Intégration |
|---|---|---|---|---|---|---|
| 0 Cadrage | C | C | C | C | R | **A** |
| 1 Données et jeu de test | **R** | C | C | C | I | **A** |
| 2 Benchmark SLM | C | I | **R** | I | C | **A** |
| 3 Vector-RAG | **R** | C | C | I | I | **A** |
| 4 KG / Graph-RAG / Hybrid | C | **R** | C | I | I | **A** |
| 5 Fine-tuning | I | I | **R** | I | I | **A** |
| 6 Optimisation d'inférence | I | I | **R** | C | C | **A** |
| 7 Multi-agents LangGraph | C | C | C | **R** | C | **A** |
| 8 Réponse automatisée | I | I | I | **R** | C | **A** |
| 9 Sécurité du LLM | I | I | C | **R** | C | **A** |
| 10 LLMOps | C | C | C | C | **R** | **A** |
| 11 Application web | C | C | I | C | **R** | **A** |
| 12 Expériences finales | **R** | **R** | **R** | **R** | **R** | **A** |
| 13 Rapport, démo, GitHub | C | C | C | C | C | **A** |

Lecture : à l'étape 12, les cinq membres exécutent (chacun ses comparaisons) et
seul le responsable d'intégration approuve le gel des résultats.

## 3. Interfaces à figer dès l'étape 0

Ces contrats sont la raison d'être du cadrage : ils permettent à cinq personnes
de travailler sans se bloquer.

| Interface | Propriétaire | Consommateur | Fichier / contrat |
|---|---|---|---|
| Schéma `Alert` et `BenchmarkCase` | M1 | tous | `data/schemas.py` (étape 1) |
| Format JSONL du jeu de test + hash | M1 | M2, M3, M4 | `data/benchmark/test.jsonl` + `test.sha256` |
| Liste d'IDs valides (anti-hallucination) | M1 | M3, M4 | `data/processed/mitre_ids.txt`, `cve_ids.txt`, `cwe_ids.txt` |
| Schéma Neo4j (nœuds/relations) | M2 | M1, M4 | `kg/schema.cypher` (étape 4) |
| Interface de retrieval (4 modes) | M1 + M2 | M4 | `rag/base.py` → `retrieve(alert) -> Context` |
| Serveur LLM (endpoint OpenAI-compatible) | M3 | M4, M5 | `models/serving/` + `.env` |
| Schéma d'action + allowlist | M4 | M5 | `security/actions.py` (étape 8) |
| Contrat d'API REST/SSE | M5 | M4 | `docs/API.md` (étape 11) |
| Format des runs et métriques | M5 | M3, M4 | `experiments/` + MLflow |

## 4. Rituels d'équipe

| Rituel | Quand | Durée | Sortie |
|---|---|---|---|
| Point de synchronisation | lundi 30 min | 30 min | ce qui est fait / bloqué / prochaine PR |
| Revue de PR | sous 24 h ouvrées | — | approbation ou demandes de modification |
| Démo interne « bout en bout » | vendredi | 15 min | le pipeline tourne, même dégradé |
| Mise à jour du README | après chaque étape | — | section rédigée à chaud, pas à la fin |

## 5. Signature de prise de rôle

En cochant, chaque membre accepte le périmètre et les interfaces ci-dessus.

- [ ] `M1` — Données & RAG — date :
- [ ] `M2` — Knowledge Graph — date :
- [ ] `M3` — Modèles & optimisation — date :
- [ ] `M4` — Agents & sécurité — date :
- [ ] `M5` — Web & LLMOps — date :
- [ ] Responsable d'intégration : ____________ — date :
