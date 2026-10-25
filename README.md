# CyberSOC AI — assistant SOC intelligent

> SLM · Hybrid RAG · Knowledge Graph · IA agentique · LLMOps
> Projet académique — équipe de 5 — échéance **01/01/2027**

Un SOC (Security Operations Center) reçoit des milliers d'alertes qu'il faut
trier, enquêter, qualifier puis traiter. Ce projet construit un assistant IA qui
automatise l'essentiel de ce travail — **sans jamais agir sans approbation
humaine** — et l'accompagne d'une étude expérimentale rigoureuse des SLM, du
Graph-RAG, de l'IA agentique, de l'optimisation d'inférence et de la sécurité
des LLM.

```
Alerte → Détection → Investigation RAG/KG → Analyse agentique → Explication
       → Évaluation du risque → Action recommandée → APPROBATION HUMAINE
       → Exécution contrôlée (sandbox) → Monitoring / Audit
```

## Statut d'avancement

| Étape | Contenu | Statut |
|---|---|---|
| 0 | Cadrage, dépôt, rôles, architecture v0, Docker | 🟡 **socle en place** — 3 points à finaliser (voir [`docs/CHECKLIST_ETAPE0.md`](docs/CHECKLIST_ETAPE0.md)) |
| 1 | Données et jeu de test | 🟡 **bloc A rédigé** — périmètre en attente de signature des 5 membres ([`docs/SCOPE.md`](docs/SCOPE.md)) |
| 2 | Benchmark des SLM | ⬜ |
| 3 | Vector-RAG | ⬜ |
| 4 | Knowledge Graph, Graph-RAG, Hybrid RAG | ⬜ |
| 5 | Fine-tuning LoRA/QLoRA | ⬜ |
| 6 | Optimisation d'inférence | ⬜ |
| 7 | Système multi-agents LangGraph | ⬜ |
| 8 | Réponse automatisée contrôlée | ⬜ |
| 9 | Sécurité du LLM | ⬜ |
| 10 | LLMOps | ⬜ |
| 11 | Application web | ⬜ |
| 12 | Expériences finales | ⬜ |
| 13 | Rapport, démo, livraison GitHub | ⬜ |

Chaque section de ce README est rédigée **au moment de l'étape correspondante**,
jamais à la fin (risque n°5 du projet).

## Architecture

Vue en couches complète et éditable : [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
· source Mermaid : [`docs/architecture/architecture_v0.mmd`](docs/architecture/architecture_v0.mmd)
· version draw.io : [`docs/architecture/architecture_v0.drawio`](docs/architecture/architecture_v0.drawio)

Couches : ingestion → connaissances (vectoriel + graphe) → retrieval (4 modes) →
modèle (SLM, LoRA, quantification, vLLM) → orchestration agentique → action
contrôlée → sécurité du LLM → interfaces et LLMOps.

## Installation

Pré-requis : Docker + Docker Compose, Python 3.10+, Git.

```bash
git clone <url-du-depot> cybersoc-ai && cd cybersoc-ai

# 1. configuration locale
cp .env.example .env            # PowerShell : Copy-Item .env.example .env

# 2. Neo4j (seul service démarré par défaut)
docker compose up -d
docker compose ps               # neo4j doit être "healthy"

# 3. vérification réelle (pas seulement le port ouvert)
docker compose exec neo4j cypher-shell -u neo4j -p changeme_local "RETURN 1 AS ok;"

# 4. environnement Python
python -m venv .venv
source .venv/bin/activate       # PowerShell : .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

# 5. vérifications
python -m pytest -q
```

Neo4j Browser : <http://localhost:7474> (identifiants dans `.env`).

Optionnel — observabilité (étape 10) :

```bash
docker compose --profile ops up -d      # ajoute MLflow sur http://localhost:5000
```

Un `Makefile` regroupe ces commandes (`make up`, `make check`, `make data`).
Sous Windows sans `make`, utiliser les commandes ci-dessus.

## Structure du dépôt

```
.
├── data/          # schémas, collecte, normalisation, benchmark annoté, datasheet
├── models/        # benchmark SLM, LoRA, quantification, serving (vLLM)
├── rag/           # chunking, embeddings, Vector-RAG, Graph-RAG, Hybrid (RRF)
├── kg/            # schéma Neo4j, imports, requêtes Cypher
├── agents/        # LangGraph : état partagé, agents, version mono-agent
├── security/      # allowlist, validation, sandbox, audit, attaques et défenses
├── backend/       # API FastAPI (alerts, investigate SSE, approve, audit)
├── frontend/      # React + TypeScript (incidents, graphe, approbation, audit)
├── experiments/   # scripts de comparaison, runs, résultats, figures
├── docs/          # architecture, rôles, règles Git, matériel, décisions (ADR)
├── tests/         # tests transverses (structure du dépôt, contrats)
└── docker-compose.yml
```

Chaque dossier possède son `README.md` décrivant son **contrat d'interface**
(entrées, sorties, propriétaire, critère de réussite). C'est ce contrat qui
permet à cinq personnes de travailler en parallèle.

## Données

> Section à rédiger à l'étape 1. Voir [`data/README.md`](data/README.md).

Trois bases de connaissances : **MITRE ATT&CK** (comment les attaquants
agissent), **CVE / CISA KEV** (quelle faille précise est exploitée), **CWE**
(quelle erreur de conception en est la cause).

## Benchmark SLM

> Section à rédiger à l'étape 2. Comparaison de SLM de 1,5 à 4 milliards de
> paramètres (Qwen2.5-3B, Phi-3.5-mini), prompt fixe, température 0, sortie JSON
> imposée, même matériel. Métriques : accuracy, précision, rappel, F1, taux
> d'hallucination, TTFT, tokens/s, mémoire.

## RAG et Knowledge Graph

> Sections à rédiger aux étapes 3 et 4. Quatre modes comparés avec le même
> script : No-RAG, Vector-RAG, Graph-RAG, Hybrid (Reciprocal Rank Fusion).

## Fine-tuning

> Section à rédiger à l'étape 5. LoRA / QLoRA, évaluation avec le protocole du
> modèle de base, sur le même jeu de test figé.

## Optimisation d'inférence

> Section à rédiger à l'étape 6. FP16 / INT8 / INT4, batching continu, prefix
> caching, Flash Attention, avec et sans KV cache, charge à 1 / 4 / 16 requêtes.

## Système multi-agents

> Section à rédiger à l'étape 7. Voir [`agents/README.md`](agents/README.md).

## Réponse automatisée

> Section à rédiger à l'étape 8. Voir [`security/README.md`](security/README.md).
> Aucune action ne s'exécute sans approbation humaine ; tout est journalisé.

## Sécurité du LLM

> Section à rédiger à l'étape 9. Tableau ASR avant/après défenses, faux positifs
> et surcoût de latence documentés.

## LLMOps

> Section à rédiger à l'étape 10. Runs MLflow, traces d'agents, versionnement des
> prompts, datasets et adaptateurs.

## Application web

> Section à rédiger à l'étape 11. Voir [`backend/README.md`](backend/README.md)
> et [`frontend/README.md`](frontend/README.md).

## Résultats et discussion

> Section à rédiger à l'étape 12 : les 6 comparaisons imposées, avec moyennes,
> écarts-types et analyse critique.

## Limites

> Section à rédiger à l'étape 12. À mentionner au minimum : données synthétiques,
> sandbox sans effet réel, taille des modèles contrainte par le matériel,
> couverture limitée à 8–12 techniques MITRE.

## Organisation de l'équipe

- Rôles, matrice RACI et interfaces figées : [`docs/ROLES.md`](docs/ROLES.md)
- Règles Git et revue : [`docs/GIT_CONVENTIONS.md`](docs/GIT_CONVENTIONS.md)
- Matériel de calcul : [`docs/HARDWARE.md`](docs/HARDWARE.md)
- Décisions techniques (ADR) : [`docs/DECISIONS.md`](docs/DECISIONS.md)
- Calendrier et jalons : [`docs/PLANNING.md`](docs/PLANNING.md)
- Checklist de l'étape 0 : [`docs/CHECKLIST_ETAPE0.md`](docs/CHECKLIST_ETAPE0.md)

### Contribution de chaque membre

> À compléter au fil du projet (une ligne par étape réalisée, reliée aux commits).

| Membre | Rôle | Étapes | Contributions principales |
|---|---|---|---|
| `M1` | Données & RAG | 1, 3 | — |
| `M2` | Knowledge Graph | 4 | — |
| `M3` | Modèles & optimisation | 2, 5, 6 | — |
| `M4` | Agents & sécurité | 7, 8, 9 | — |
| `M5` | Web & LLMOps | 10, 11 | — |

## Licence et sources

> À compléter à l'étape 13 : licence du dépôt, licences des jeux de données
> (MITRE ATT&CK, CISA KEV, CWE, CTI) et conditions de réutilisation.
