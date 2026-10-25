# Règles Git et revue de code

Règles imposées par la feuille de route (étape 0, tâche 3) :
**une branche par tâche, une pull request relue par un autre membre, un commit par tâche.**

## 1. Branches

Format : `<type>/<etape>-<sujet-court>` en kebab-case.

```
feat/1-datasets-mitre
feat/3-vector-rag-chroma
feat/4-schema-neo4j
fix/2-hallucination-parsing
docs/0-roles
chore/0-ci
exp/12-benchmark-final
```

| Préfixe | Usage |
|---|---|
| `feat/` | nouvelle fonctionnalité |
| `fix/` | correction de bug |
| `exp/` | expérience jetable (résultats dans `experiments/`, pas de code de prod) |
| `docs/` | documentation seule |
| `chore/` | outillage, CI, dépendances |
| `refactor/` | réécriture sans changement de comportement |

`main` est protégée : pas de push direct, pas de force-push, PR obligatoire.

## 2. Commits

Un commit par tâche signifie : un commit par PR, avec un message qui décrit la
tâche accomplie. Convention [Conventional Commits](https://www.conventionalcommits.org/) :

```
<type>(<scope>): <description à l'impératif, ≤ 72 caractères>

<corps optionnel : pourquoi, pas comment>

Refs: #12
```

Exemples conformes :

```
feat(data): normaliser MITRE ATT&CK en JSONL
feat(kg): créer le schéma Neo4j des entités SOC
fix(rag): corriger le calcul de Recall@k sur les k plus grands que l'index
docs(roles): figer la matrice RACI des 5 rôles
```

Un commit doit laisser le dépôt dans un état qui passe `make check`.
Si vous avez plusieurs commits en cours de route, vous pouvez les fusionner
avant la revue (`git rebase -i origin/main`) pour respecter « un commit par tâche ».

## 3. Pull requests

Checklist du modèle de PR (`.github/PULL_REQUEST_TEMPLATE.md`) :

1. La PR traite **une seule** tâche de la feuille de route (indiquer le numéro d'étape).
2. `make check` passe localement.
3. Un autre membre a relu et approuvé — jamais l'auteur.
4. Les données ajoutées sont justifiées (poids, licence, hash).
5. La section de README correspondante est mise à jour si l'étape en produit une.

Fusion : **rebase and merge** (pas de squash) pour conserver exactement un
commit par tâche et un historique linéaire.

## 4. Ce qui ne rentre jamais dans Git

- Poids de modèles (`*.safetensors`, `*.gguf`, `*.bin`, `*.pt`) : voir `models/MANIFEST.md`.
- `data/raw/` et `data/interim/` : reconstructibles par `make data`.
- `.env`, clés, jetons : `.env.example` sert de documentation.
- Volumes Docker (`kg/neo4j_data/`).

## 5. Fichiers de données versionnés

Les jeux de test étant le socle de toutes les expériences, ils **sont**
versionnés dans `data/benchmark/` et `data/processed/`, avec :

- un fichier `*.sha256` à côté de chaque jeu figé ;
- une entrée dans `data/DATASHEET.md` (sources, licences, méthode, limites).

Toute modification d'un jeu figé exige une PR dédiée, un bump de version du
fichier (`test.v2.jsonl`) et la mise à jour du hash dans `docs/DECISIONS.md`.

## 6. Gestion des conflits

- `data/benchmark/`, `docs/DECISIONS.md` et `docker-compose.yml` sont des
  fichiers à forte contention : prévenir le responsable d'intégration avant
  d'y toucher.
- Les fichiers JSONL longs se résolvent en régénérant (`make data`) plutôt
  qu'en fusionnant à la main.
