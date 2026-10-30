# `data/` — Données et jeu de test

**Casquette** : Données & RAG · **Étapes** : 1 (puis lecture seule)
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
├── schemas.py      # Alert, BenchmarkCase, RetrievalQA (Pydantic v2)   [bloc C]
├── sources.py      # registre des sources + téléchargement + SHA-256    ✅ bloc B
├── ingest.py       # normalisation STIX / KEV / CWE -> JSONL            ✅ bloc B
├── chunking.py     # découpage 300–500 tokens avec chevauchement        ✅ bloc B
├── build_all.py    # pipeline complet de `make data`                    ✅ bloc B
├── DATASHEET.md    # sources, licences, méthode, répartition, limites  [bloc E]
├── scope.json      # périmètre figé : techniques, alertes, actions, sévérités  ✅ bloc A
└── validate_scope.py  # contrôle de cohérence du périmètre (stdlib, exécutable) ✅ bloc A
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

## Bloc B — ce qui est produit, et ses limites

Sorties de `make data` (chiffres issus du manifeste, à date du 2026-10-25) :

| Fichier | Contenu | Volume |
|---|---|---|
| `processed/mitre_techniques.jsonl` | techniques et sous-techniques ATT&CK | 867 |
| `processed/mitre_groupes.jsonl` | groupes APT + techniques observées | 193 |
| `processed/mitre_logiciels.jsonl` | malwares et outils | 845 |
| `processed/mitre_campagnes.jsonl` | campagnes | 57 |
| `processed/kev_cves.jsonl` | CVE du catalogue CISA KEV | 1 756 |
| `processed/cwe_faiblesses.jsonl` | faiblesses CWE | 969 |
| `processed/chunks.jsonl` | corpus indexable — **non versionné**, régénéré par `make data`, empreinte SHA-256 dans le manifeste | 4 842 chunks (23–500 tokens, moyenne 189) |
| `processed/{mitre,cve,cwe}_ids.txt` | identifiants valides | 1 962 / 1 756 / 969 |
| `processed/sources_manifest.json` | SHA-256, licences, compteurs | — |

**Cinq décisions à connaître** (elles sont aussi notées dans le manifeste) :

1. **Comptage de tokens approximatif** (4 caractères = 1 token), déclaré dans chaque chunk via `tokenizer: "approx_chars_div_4"`. L'étape 3 pourra le recalculer avec le tokenizer réel sans casser les comparaisons.
2. **`cve_ids.txt` = KEV uniquement.** Une CVE réelle absente de KEV n'y figure pas : la métrique d'hallucination de l'étape 2 mesure donc « identifiant valide **dans le périmètre de connaissance du système** », pas « CVE existante ». À écrire noir sur blanc dans le rapport, sinon la métrique sera contestée.
3. **Objets obsolètes ou révoqués** : exclus du corpus indexé (sinon on apprend au modèle des techniques retirées), mais **conservés** dans les listes d'identifiants — un ID retiré reste un ID réel, donc pas une hallucination.
4. **Corpus CTI** : OTX et abuse.ch exigent une clé d'API (non disponible à ce stade). Le rôle de corpus CTI est tenu par les **groupes et campagnes ATT&CK** (193 + 57 rapports en texte libre), qui sont publics et déjà rattachés aux techniques. Le branchement OTX pourra être ajouté sans changer le format des chunks.
5. **Licences non confirmées** : aucune des trois sources ne publie de fichier de licence explicite dans son dépôt. Le manifeste le signale ; la confirmation appartient à `DATASHEET.md` (bloc E) avant toute publication du rapport.

6. **`chunks.jsonl` n'est pas versionné.** C'est un artefact dérivé de 5,5 Mo : `python -m data.build_all --offline` le reconstruit à l'identique, et le manifeste publie son SHA-256 (section `chunks`). Vérification en une commande :

```bash
python -m data.build_all --offline
python -c "import json,hashlib,pathlib; m=json.load(open('data/processed/sources_manifest.json')); f=pathlib.Path('data/processed/chunks.jsonl'); print('identique' if hashlib.sha256(f.read_bytes()).hexdigest()==m['chunks']['sha256'] else 'DIVERGENT')"
```

## Critère de réussite de l'étape 1

- aucun `scenario_id` commun entre train et test ;
- kappa de Cohen > 0,8 sur 50 cas doublement annotés ;
- un membre extérieur à l'étape relance `make data` avec succès.

## Pièges connus

- jeu trop facile (tous les cas malveillants contiennent « malware ») ;
- déséquilibre de classes non mesuré ;
- fuite train/test par quasi-doublons (utiliser `rapidfuzz`) ;
- entités synthétiques absentes du graphe (coordonner avec la casquette Knowledge Graph dès la semaine 1).
