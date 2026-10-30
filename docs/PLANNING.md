# Calendrier du projet — mené seul

Échéance finale : **01/01/2027**. Projet individuel : les étapes s'enchaînent,
elles ne se parallélisent pas. Semaine 1 = 26 octobre – 1er novembre 2026.

## 1. Le cadrage temporel, sans illusion

| | |
|---|---|
| Jours calendaires restants (30 oct → 1er jan) | 63 |
| Jours ouvrés réellement travaillables | **≈ 43** |
| Travail estimé (voir [`ROLES.md`](ROLES.md) § 2) | ≈ 67 j |
| Écart | **≈ −24 j** |

Le plan ci-dessous n'est donc pas « tout faire » : c'est **tout couvrir, en
réduisant la profondeur aux endroits choisis d'avance** dans [`ROLES.md`](ROLES.md) § 4.

## 2. Semaines

| Sem. | Dates | Objectif | Livrable vérifiable | Risque |
|---|---|---|---|---|
| **S1** | 26 oct – 1 nov | Cadrage, périmètre, socle de données — *en cours* | dépôt, `scope.json` gelé, corpus (4 842 chunks), 3 listes d'IDs | faible |
| **S2** | 2 – 8 nov | Blocs C, D, E : schémas, monde simulé, 250 cas annotés | `test.jsonl` figé + `test.sha256` + `DATASHEET.md` | **élevé** — l'annotation est longue |
| **S3** | 9 – 15 nov | Étape 2 : benchmark Qwen vs Phi (no-RAG), hallucinations | tableau comparatif + 1re section du rapport | moyen — dépend du GPU |
| **S4** | 16 – 22 nov | Étape 3 : Vector-RAG, Recall@k, MRR | 4 modes comparés sur le test figé | moyen — **GO/NO-GO au 22 nov** |
| **S5** | 23 – 29 nov | Étape 4 : Neo4j, Graph-RAG, Hybrid RRF | schéma peuplé + 3 requêtes Cypher utiles | moyen |
| **S6** | 30 nov – 6 déc | Étape 5 : LoRA (+ démarrage du rapport) | adaptateur + manifeste + gain mesuré | **élevé** — GPU |
| **S7** | 7 – 13 déc | Étape 6 : INT8/INT4, latence, coût (+ étape 7 amorcée) | tableau précision/latence/mémoire | moyen |
| **S8** | 14 – 20 déc | Étape 7 : agents LangGraph + étape 8 : actions contrôlées | démo du fil rouge de bout en bout | **élevé** — intégration |
| **S9** | 21 – 27 déc | Étape 9 sécurité + étape 10 LLMOps + étape 11 app | 5 attaques bloquées + 2 écrans | élevé |
| **S10** | 28 déc – 1 jan | Étape 12 campagne finale + étape 13 rapport + étape 14 démo | rapport complet + vidéo | **très élevé** |

Le rapport **commence en S6**, une section par semaine. Tout le rédiger en S10 est
la première cause d'échec dans ce type de projet.

## 3. Points de non-retour (go / no-go)

| Date | Condition | Si non remplie |
|---|---|---|
| **8 nov** | jeu de test figé et hashé | on réduit le benchmark à 250 cas et on passe quand même : sans test figé, aucune comparaison n'a de valeur |
| **22 nov** | étape 2 mesurée (au moins un modèle, mode no-RAG) | on abandonne le Graph-RAG profond ; le KG reste une perspective documentée |
| **13 déc** | LoRA démarré ou abandon assumé | on abandonne le fine-tuning et on s'appuie sur la comparaison few-shot déjà mesurée |
| **20 déc** | fil rouge exécutable en ligne de commande | l'application web est remplacée par une démo CLI + captures, documentée comme limite |

## 4. Ce qui est buffer, et ce qui ne l'est pas

Il n'y a **pas de semaine tampon**. Le seul amortisseur est le tri du § 4 de
[`ROLES.md`](ROLES.md). Corollaire : une semaine perdue n'est pas rattrapable par
du travail supplémentaire, elle se rattrape en réduisant le périmètre — décision
qui doit être prise **le dimanche même**, pas trois semaines plus tard.

## 5. Suivi hebdomadaire

À remplir chaque dimanche, trois lignes (fait / en retard / décision).

| Sem. | Fait | En retard | Décision |
|---|---|---|---|
| S1 | | | |
| S2 | | | |
| S3 | | | |
| S4 | | | |
| S5 | | | |
| S6 | | | |
| S7 | | | |
| S8 | | | |
| S9 | | | |
| S10 | | | |

## 6. Jalons du rapport

| Jalon | Date | Contenu minimal |
|---|---|---|
| Plan détaillé | 8 nov | sommaire figé, sections attribuées aux casquettes |
| Chapitres 3 à 6 rédigés | 6 déc | données, benchmark, RAG/KG |
| Chapitres 7 à 11 rédigés | 20 déc | agents, actions, sécurité, LLMOps, application |
| Résultats et discussion | 27 déc | tableaux de l'étape 12, limites |
| Relecture finale + dépôt | 31 déc | mise en forme, bibliographie, annexes |
