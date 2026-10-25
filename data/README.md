# `data/` — Données et jeu de test

**Rôle propriétaire** : M1 (Données & RAG) · **Étapes** : 1 (puis lecture seule)
**C'est le module le plus critique du projet** : un jeu de test faible ou pollué
invalide toutes les comparaisons des étapes 2 à 12.

## Contrat d'interface

| Entrée | Sortie |
|---|---|
| sources publiques (MITRE ATT&CK STIX, CISA KEV, CWE, CTI) | `processed/*.jsonl` normalisés |
| graine aléatoire `RANDOM_SEED` | `benchmark/{train,val,test}.jsonl` + `test.sha256` |
| — | listes d'IDs valides pour la détection d'hallucination |

## Arborescence

```
data/
├── raw/            # téléchargements bruts (NON versionné, reconstructible)
├── interim/        # étapes intermédiaires de nettoyage (NON versionné)
├── processed/      # JSONL normalisés + mitre_ids.txt, cve_ids.txt, cwe_ids.txt (versionné)
├── benchmark/      # train/val/test + retrieval_qa.jsonl + hashes (versionné)
├── schemas.py      # Alert, BenchmarkCase, RetrievalQA (Pydantic v2)   [étape 1]
├── build_all.py    # point d'entrée de `make data`                     [étape 1]
├── DATASHEET.md    # sources, licences, méthode, répartition, limites  [étape 1]
└── scope.json      # périmètre figé : techniques MITRE, actions, sévérités [étape 1]
```

## Ce qui est versionné et ce qui ne l'est pas

- **Versionné** : `processed/`, `benchmark/`, `schemas.py`, `DATASHEET.md`, `scope.json`, les scripts.
- **Non versionné** : `raw/`, `interim/` — reconstruits à l'identique par `make data`.

## Règles non négociables

1. `scenario_id` obligatoire sur chaque cas : le split se fait **par scénario**, jamais par ligne (ADR-0005).
2. Toute modification d'un fichier de `benchmark/` exige une PR dédiée et un nouveau hash SHA-256.
3. 40 à 50 % de cas bénins, plusieurs niveaux de difficulté (facile / moyen / difficile).
4. Chaque scénario malveillant a un **jumeau bénin** (ex. PowerShell d'un administrateur depuis le VPN).
5. `DATASHEET.md` est un livrable, pas un bonus : sans lui, l'étape 1 n'est pas terminée.

## Critère de réussite de l'étape 1

- aucun `scenario_id` commun entre train et test ;
- kappa de Cohen > 0,8 sur 50 cas doublement annotés ;
- un membre extérieur à l'étape relance `make data` avec succès.

## Pièges connus

- jeu trop facile (tous les cas malveillants contiennent « malware ») ;
- déséquilibre de classes non mesuré ;
- fuite train/test par quasi-doublons (utiliser `rapidfuzz`) ;
- entités synthétiques absentes du graphe (coordonner avec M2 dès la semaine 1).
