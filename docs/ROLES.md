# Rôles du projet — une personne, cinq casquettes

> **Projet individuel.** La feuille de route prévoyait cinq membres ; le projet
> est mené seul. Les cinq rôles sont conservés comme **casquettes** : ils restent
> la grille de lecture des compétences attendues et la structure du rapport, mais
> ils sont portés par la même personne, **séquentiellement** et non en parallèle.
> C'est cette absence de parallélisme qui crée le risque principal — la charge —
> traité au § 4.

## 1. Pourquoi garder cinq casquettes plutôt qu'un rôle unique

1. **Lisibilité de la couverture.** Le jury attend cinq compétences (données,
   graphes, modèles, agents/sécurité, web/LLMOps). Les nommer rend la couverture
   vérifiable au lieu de la laisser deviner.
2. **Contrats d'interface explicites.** Chaque casquette laisse derrière elle un
   contrat écrit (§ 5). En changeant de casquette, on reprend le contrat, pas sa
   mémoire — ce qui compte quand trois semaines séparent l'amont de l'aval.
3. **Traçabilité honnête.** Le rapport peut dire « j'ai assuré les cinq
   casquettes, voici comment je les ai séquencées et ce que j'ai réduit », au lieu
   de laisser croire à une équipe.

## 2. Les cinq casquettes

Estimations en **jours de travail effectif**, à réviser après la semaine 2.

| # | Casquette | Périmètre | Étapes | Effort estimé | Semaines |
|---|---|---|---|---|---|
| 1 | **Données & RAG** | collecte MITRE/KEV/CWE, normalisation, chunking, embeddings, Vector-RAG, listes d'IDs valides, annotation, datasheet | 1, 3 | 14 j | S1–S2, S4 |
| 2 | **Knowledge Graph** | schéma Neo4j, import, requêtes Cypher, Graph-RAG, fusion RRF | 4 | 5 j | S5 |
| 3 | **Modèles & optimisation** | benchmark SLM, LoRA/QLoRA, quantification FP16/INT8/INT4, vLLM, latence et coût | 2, 5, 6 | 13 j | S3, S6, S7 |
| 4 | **Agents & sécurité** | LangGraph, sandbox d'actions, allowlist, jeu d'attaques et défenses LLM | 7, 8, 9 | 11 j | S7–S9 |
| 5 | **Web & LLMOps** | FastAPI, React/TypeScript, MLflow/Langfuse, journal d'audit, démo | 10, 11 | 8 j | S9 |
| + | **Responsable d'intégration** (transverse) | point de passage unique pour `main`, arbitrage des interfaces, garde du calendrier, propriétaire du README | toutes | 4 j répartis | continu |
| | **Rapport et soutenance** | rédaction, figures, démo vidéo, préparation | 13, 14 | 12 j | S6–S10 |

**Total ≈ 67 jours de travail effectif.**

## 3. La contrainte arithmétique

Du 30 octobre au 1er janvier : 63 jours calendaires, dont **≈ 43 jours ouvrés**
réellement travaillables (week-ends et fêtes déduits).

| Poste | Jours |
|---|---|
| Travail estimé (§ 2) | ≈ 67 |
| Jours ouvrés disponibles | ≈ 43 |
| **Écart** | **≈ −24** |

Même avec les durées les plus basses de la feuille de route (2 jours par étape :
14 × 2 = 28 j, plus rapport et soutenance), on atteint ~43 jours : **il n'y a
aucun gras**. La conclusion est structurelle : le projet ne peut pas être livré
« en entier et en profondeur ». Il doit être livré **entier en couverture, réduit
en profondeur sur les points choisis d'avance** — et ce choix doit être écrit
avant d'être subi (§ 4).

## 4. Ce qui est sacrifié si le temps manque (dans cet ordre)

À appliquer **dans cet ordre**, sans improviser au dernier moment.

| Rang | Ce qui est réduit | Forme dégradée retenue | Déclencheur |
|---|---|---|---|
| 1 | Langfuse et MLflow avancé | MLflow local minimal (runs + métriques), traces d'agent dans des fichiers JSONL | S9 |
| 2 | Graph-RAG profond | 3 requêtes Cypher utiles au lieu de 10 ; le graphe reste peuplé et explorable | S5 |
| 3 | Application web | 2 écrans (liste + détail d'incident) au lieu de 5 | S9 |
| 4 | Red-team LLM | 5 attaques représentatives au lieu de 15 | S9 |
| 5 | Fine-tuning LoRA | comparaison few-shot déjà mesurée à l'étape 2 + justification écrite de l'abandon | S6, si GPU indisponible |
| — | **Jamais réduit** | jeu de test figé et hashé, allowlist et validation des actions, mesure des hallucinations, honnêteté des limites dans le rapport | — |

La règle : **on réduit la profondeur, jamais la rigueur de mesure.** Un Graph-RAG
à trois requêtes correctement évalué vaut mieux qu'un Graph-RAG à dix requêtes
non mesuré.

## 5. Contrats d'interface entre casquettes

Ce sont les seuls points de passage. Un contrat change = on incrémente le
document, pas le code en silence.

| Interface | Casquette amont | Casquette aval | Emplacement |
|---|---|---|---|
| Schéma `Alert` et `BenchmarkCase` | Données & RAG | toutes | `data/schemas.py` (bloc C) |
| Format JSONL du jeu de test + hash | Données & RAG | Modèles, Agents | `data/benchmark/test.jsonl` + `test.sha256` |
| Liste d'IDs valides (anti-hallucination) | Données & RAG | Modèles, Agents | `data/processed/*_ids.txt` |
| Schéma Neo4j (nœuds/relations) | Knowledge Graph | Données, Agents | `kg/schema.cypher` (étape 4) |
| Interface de retrieval (4 modes) | Données & RAG + Knowledge Graph | Agents | `rag/base.py` → `retrieve(alert, mode) -> Context` |
| Serveur LLM (endpoint OpenAI-compatible) | Modèles & optimisation | Agents, Web | `models/serving/` + `.env` |
| Schéma d'action + allowlist | Agents & sécurité | Web | `security/actions.py` (étape 8) |
| Contrat d'API REST/SSE | Web & LLMOps | Agents & sécurité | `docs/API.md` (étape 11) |
| Format des runs et métriques | Web & LLMOps | Modèles, Agents | `experiments/` + MLflow |

## 6. Rythme de travail

Hypothèse de planification : **6 demi-journées utiles par semaine**, week-ends
inclus par moitié. Toute semaine n'atteignant pas ce volume décale la chaîne
d'une semaine entière, puisque rien n'est parallélisable.

Point de contrôle **chaque dimanche**, trois lignes :

```
Fait :
En retard :
Décision prise (et pourquoi) :
```

## 7. Journal des décisions d'organisation

| Date | Décision | Raison |
|---|---|---|
| 2026-10-25 | Dépôt structuré en 10 modules avec contrats écrits | prévu pour 5, conservé seul : les contrats restent utiles pour l'auteur à J+21 |
| 2026-10-30 | Validation du périmètre par revue en 3 passes au lieu de 5 signatures | projet individuel ; le gel par tag Git remplace la preuve sociale |
| 2026-10-30 | Cinq casquettes conservées, portées séquentiellement | lisibilité de la couverture des compétences, sans fictive parallélisation |
