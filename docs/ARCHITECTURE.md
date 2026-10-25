# Architecture v0 — CyberSOC AI

> Document de référence de l'étape 0. Il sera réutilisé (et affiné) dans le
> rapport final. Version : **v0** — figée le 2026-10-25, à réviser aux étapes 4, 7 et 11.
>
> Fichiers : [`architecture_v0.mmd`](architecture/architecture_v0.mmd) (source Mermaid),
> [`architecture_v0.drawio`](architecture/architecture_v0.drawio) (éditable draw.io / diagrams.net).

## 1. Chaîne fonctionnelle (fil rouge)

Alerte → Détection → Investigation RAG/KG → Analyse agentique → Explication →
Évaluation du risque → Action recommandée → **Approbation humaine** →
Exécution contrôlée (sandbox) → Monitoring / Audit.

Le système n'exécute jamais une action seul : l'approbation humaine est un
point d'arrêt structurel du graphe d'agents (`interrupt_before`), pas une
simple politique applicative.

## 2. Vue en couches

```mermaid
flowchart TB
    classDef store fill:#e8f0fe,stroke:#1a56db,stroke-width:1px
    classDef sec fill:#fde8e8,stroke:#c81e1e,stroke-width:1px
    classDef svc fill:#e6f4ea,stroke:#137333,stroke-width:1px
    classDef human fill:#fff4e5,stroke:#b45309,stroke-width:1px,stroke-dasharray: 4 2

    subgraph L1["① Ingestion — étape 1"]
        A1["Alerte brute<br/>EVTX / JSON / SIEM"] --> A2["Normalisation<br/>schéma Alert (Pydantic)"]
        A2 --> A3["Extraction d'entités<br/>IP · host · user · hash · CVE"]
    end

    subgraph L2["② Connaissances — étapes 1, 3, 4"]
        S1["Sources<br/>MITRE ATTACK · CISA KEV<br/>CWE · threat intel"] --> S2["Chunks 300–500 tokens<br/>+ métadonnées"]
        S2 --> VEC[("Vector store<br/>Chroma")]:::store
        S1 --> G1["Import STIX<br/>techniques · groupes · malwares"]
        G1 --> KG[("Neo4j<br/>Knowledge Graph")]:::store
        S1 --> IDS["Listes d'IDs valides<br/>mitre_ids · cve_ids · cwe_ids"]
    end

    subgraph L3["③ Retrieval — étapes 3 et 4"]
        M1["No-RAG"]
        M2["Vector-RAG<br/>top-k sémantique"]
        M3["Graph-RAG<br/>sous-graphe → texte"]
        M4["Hybrid<br/>RRF(vecteur, graphe)"]
    end

    subgraph L4["④ Modèle — étapes 2, 5, 6"]
        P1["Prompt système SOC<br/>sortie JSON stricte"]
        P2["SLM Qwen2.5-3B<br/>Phi-3.5-mini"]
        P3["Adaptateur LoRA<br/>(étape 5)"]
        P4["Quantification<br/>FP16 · INT8 · INT4"]
        P5["vLLM<br/>batching · prefix cache"]:::svc
    end

    subgraph L5["⑤ Orchestration agentique — étape 7 (LangGraph)"]
        O1["Triage"] --> O2["Investigation (orchestrateur)"]
        O2 --> O3["Agent RAG"]
        O2 --> O4["Agent Knowledge Graph"]
        O2 --> O5["Agent Threat Intel"]
        O3 --> O6["Response"]
        O4 --> O6
        O5 --> O6
        O7["Checkpointer<br/>état partagé"]:::store
    end

    subgraph L6["⑥ Action contrôlée — étape 8"]
        R1["Action structurée<br/>type · cible · preuve · risque"] --> R2{"Validation<br/>allowlist · cible connue<br/>ressource non protégée"}
        R2 -->|refus| R9["Rejet tracé"]
        R2 -->|acceptée| R3["PENDING"]:::human
        R3 --> R4["Approbation analyste"]:::human
        R4 -->|approuvée| R5["Exécution sandbox<br/>(état simulé)"]:::svc
        R4 -->|rejetée| R9
        R5 --> R6["Journal d'audit<br/>proposée → validée → approuvée → exécutée"]:::store
    end

    subgraph L7["⑦ Sécurité du LLM — étape 9"]
        SEC1["Délimiteurs contenu non fiable<br/>détecteur d'injection"]:::sec
        SEC2["Validation de sortie<br/>schéma + IDs existants"]:::sec
        SEC3["Masquage secrets / PII<br/>filtre de sortie"]:::sec
        SEC4["Allowlist d'outils<br/>moindre privilège"]:::sec
    end

    subgraph L8["⑧ Interfaces & LLMOps — étapes 10, 11"]
        W1["FastAPI<br/>/alerts · /investigate (SSE)<br/>/actions/approve · /audit"]:::svc
        W2["React + TypeScript<br/>incidents · graphe · approbation"]:::svc
        W3["MLflow · Langfuse<br/>runs · traces d'agents"]:::store
    end

    A3 --> O1
    VEC --> M2
    KG --> M3
    M2 --> M4
    M3 --> M4
    IDS -.->|anti-hallucination| P1
    M1 --> P2
    M2 --> P2
    M3 --> P2
    M4 --> P2
    P1 --> P2 --> P3 --> P4 --> P5
    P5 --> O3
    P5 --> O4
    P5 --> O5
    O6 --> R1
    O7 -.-> O2
    R1 -.-> SEC1
    R1 -.-> SEC2
    R1 -.-> SEC4
    W1 <--> O2
    W2 <--> W1
    O2 -.-> W3

## 3. Séquence du fil rouge ALR-0042

```mermaid
sequenceDiagram
    autonumber
    participant SIEM as SIEM / source
    participant API as FastAPI
    participant G as LangGraph (état partagé)
    participant RAG as Vector + Graph RAG
    participant LLM as SLM (vLLM)
    participant SEC as Module sécurité
    participant AN as Analyste (IHM)
    participant SBX as Sandbox

    SIEM->>API: POST /alerts (ALR-0042)
    API->>G: démarrage du workflow
    G->>G: Triage (priorité haute ?)
    G->>RAG: entités + requête (powershell -enc depuis WINWORD)
    RAG-->>G: T1059.001, T1204.002, CVE proches, voisins du graphe
    G->>LLM: contexte délimité + consigne JSON
    LLM-->>SEC: JSON proposé (mitre, risque, action)
    SEC->>SEC: IDs existants ? schéma valide ? action autorisée ?
    SEC-->>G: sortie validée ou rejetée
    G-->>AN: explication + score de risque + action recommandée
    Note over G: interruption avant l'agent Response (human-in-the-loop)
    AN->>API: POST /actions/ACT-0042-1/approve
    API->>SBX: isolate_host WKS-FIN-07
    SBX-->>API: résultat simulé + journal d'audit
```

## 4. Portée de chaque module

| Module | Contenu | Ce qu'il ne fait pas |
|---|---|---|
| `data/` | schémas Pydantic, collecte, normalisation, monde simulé, benchmark, datasheet | ne fait aucun appel LLM |
| `models/` | benchmark SLM, adaptateurs LoRA, scripts de quantification et de serving | ne connaît ni les alertes ni le graphe |
| `rag/` | chunking, embeddings, index vectoriel, 4 modes de retrieval, métriques | ne décide pas de l'action |
| `kg/` | schéma Neo4j, import, requêtes Cypher, export de sous-graphe | ne génère pas de texte libre |
| `agents/` | graphe LangGraph, état partagé, agents spécialisés, version mono-agent | n'exécute aucun effet de bord |
| `security/` | allowlist d'actions, validation, sandbox, jeux d'attaques, défenses | ne décide pas de l'investigation |
| `backend/` | API FastAPI, SSE, persistance de l'audit | ne contient pas de logique d'IA |
| `frontend/` | React/TS, visualisation du graphe, approbation | pas d'accès direct au LLM |
| `experiments/` | scripts de comparaison, résultats CSV/JSON, figures | pas de code de production |

## 5. Choix structurants (et ce qui reste ouvert)

| Sujet | Décision v0 | Justification | Revoir à |
|---|---|---|---|
| Dépôt | monorepo, 10 dossiers imposés | le sujet l'impose ; facilite l'intégration à 5 | — |
| Conteneurisation | Docker Compose, Neo4j seul par défaut, observabilité dans le profil `ops` | critère étape 0 = `docker compose up` sur 5 machines, souvent modestes | étape 10 |
| Base graphe | Neo4j 5 | imposé par le sujet, écosystème Cypher mature | étape 4 |
| Base vectorielle | **non figée** (Chroma pressenti) | dépendra du volume réel de chunks et des mesures de l'étape 3 | étape 3 |
| Contrat d'échange | Pydantic v2 partout, JSONL sur disque | schémas stricts = validation des sorties LLM (étape 9) | — |
| Identité des données | `scenario_id` obligatoire dès le premier jour | condition du split anti-fuite ; rétro-fitter serait coûteux | — |
| Exécution des actions | sandbox uniquement, jamais de commande système | exigence d'auditabilité et de sécurité | — |

## 6. Décisions volontairement différées

Ne pas trancher maintenant évite de bloquer l'équipe sur des choix qui
dépendent de mesures qui n'existent pas encore :

1. **Modèle d'embeddings** (BGE / E5 / GTE / MiniLM) → étape 3, après mesure de Recall@k.
2. **Taille de chunk définitive** → étape 3 (300–500 tokens est une fourchette de départ).
3. **INT8 ou INT4** → étape 6, après `docs/HARDWARE.md` et mesures de F1.
4. **Librairie d'orchestration retriever** (LangChain vs LlamaIndex vs appels directs) → étape 4.
5. **MLflow vs W&B, Langfuse vs LangSmith** → étape 10 (MLflow retenu par défaut car local et gratuit).
6. **Ajout d'un 3e SLM au benchmark** → étape 2, seulement si la VRAM le permet.
