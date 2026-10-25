# Calendrier du projet

Échéance finale : **01/01/2027**. Équipe de 5. Semaine 1 = 26 octobre – 1er novembre 2026.

## 1. Vue par semaine

| Semaine | Dates approx. | Étapes principales | Jalon de sortie |
|---|---|---|---|
| 1 | 26 oct – 1 nov | **0**, début de 1 | dépôt + rôles + architecture v0 ; Neo4j démarre chez les 5 |
| 2 | 2 – 8 nov | 1, 2 | jeu de test figé et hashé ; premier tableau de benchmark |
| 3 | 9 – 15 nov | 2, 3, 4 | Vector-RAG mesuré ; schéma Neo4j peuplé |
| 4 | 16 – 22 nov | 3, 4, 5, 6 | **pipeline minimal de bout en bout** (risque n°1) |
| 5 | 23 – 29 nov | 4, 5, 6, 7, 10 | Hybrid RAG + adaptateur LoRA versionné |
| 6 | 30 nov – 6 déc | 6, 7, 8, 11 | 4 modes de RAG comparés sur le même script |
| 7 | 7 – 13 déc | 7, 8, 9, 11 | workflow multi-agents complet avec approbation humaine |
| 8 | 14 – 20 déc | 9, 10, 11, début de 12 | tableau ASR avant/après défenses |
| 9 | 21 – 27 déc | 12, 13 | 6 comparaisons finales + README |
| Marge | 28 – 31 déc | finalisation | vidéo, test sur machine propre, livraison |

## 2. Jalons de contrôle

| Jalon | Date cible | Critère vérifiable |
|---|---|---|
| J0 — Cadrage terminé | 1 nov 2026 | `docker compose up` démarre Neo4j chez les 5 ; rôles signés ; architecture v0 commitée |
| J1 — Données gelées | 8 nov 2026 | `test.jsonl` + hash + kappa > 0,8 ; `make data` relancé par un non-auteur |
| J2 — Pipeline bout en bout | 22 nov 2026 | une alerte traverse alerte → RAG → action structurée, même dégradée |
| J3 — Système complet | 13 déc 2026 | parcours complet dans l'interface web, approbation + sandbox + audit |
| J4 — Résultats gelés | 27 déc 2026 | 6 comparaisons × 3 répétitions, moyennes et écarts-types |
| J5 — Livraison | 31 déc 2026 | dépôt propre, README complet, vidéo ≤ 5 min |

## 3. Chemin critique

```
étape 1 (données) ─┬─> étape 2 (benchmark) ─> étape 5 ─> étape 12
                   ├─> étape 3 (Vector) ─┐
                   └─> étape 4 (KG) ─────┴─> étape 7 ─> étape 8 ─> étape 11 ─> étape 12
                                              étape 9 ─┘        étape 6 ─────┘
```

L'étape 1 bloque presque tout : toute dérive sur les données se propage
directement à l'étape 12. C'est le seul livrable pour lequel il ne faut pas
« voir plus tard ».

## 4. Les 5 risques et leur parade

| # | Risque | Parade concrète |
|---|---|---|
| 1 | Intégrer trop tard | jalon J2 (semaine 4) : pipeline minimal obligatoire, même en mode dégradé |
| 2 | Jeu de test faible ou fuite train/test | split par `scenario_id`, hash SHA-256, contrôle de doublons, kappa > 0,8 avant de continuer |
| 3 | Expériences non tracées | MLflow configuré dès la semaine 1 (profil `ops`), un run par résultat du rapport |
| 4 | Modèles trop gros pour le matériel | plafond 1,5–4 Md de paramètres, arbitrage INT4/INT8 figé après `docs/HARDWARE.md` |
| 5 | Rapport rédigé à la fin | chaque section du README est écrite dans la PR de l'étape correspondante |
