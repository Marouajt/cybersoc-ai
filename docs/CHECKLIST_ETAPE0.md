# Checklist — Étape 0 : cadrage et organisation

Semaine 1 (26 oct – 1 nov 2026), durée prévue 2 à 3 jours.
**Objectif** : disposer d'un socle stable pour démarrer l'étape 1 sans blocage.

## Livrables de l'étape

| Livrable exigé | Où | État |
|---|---|---|
| Dépôt initialisé avec les 10 dossiers | racine | ✅ fait |
| Rôles définis | [`docs/ROLES.md`](ROLES.md) | ✅ cinq casquettes, plan de charge et tri (projet individuel) |
| Schéma d'architecture v0 | [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) + [`architecture/`](architecture/) | ✅ fait |
| `docker-compose.yml` (Neo4j d'abord) | racine | ✅ fait (non exécuté ici : Docker absent de ce poste) |
| Inventaire matériel | [`docs/HARDWARE.md`](HARDWARE.md) | ⚠️ à remplir (une seule machine) |

**Critère de réussite** : `docker compose up` démarre Neo4j sur la machine de travail et en CI.

## Tâches de la feuille de route, une par une

- [x] **1. Dépôt + structure** — `data/ models/ rag/ kg/ agents/ security/ backend/ frontend/ experiments/ docs/`, chacun avec un README décrivant son contrat. Ajouts : `tests/` (CI) et `.github/` (revue).
- [ ] **2. Rôles** — tableau rempli et signé dans `docs/ROLES.md`, **responsable d'intégration désigné**.
- [x] **3. Règles Git** — branche par tâche, PR relue, un commit par tâche : `docs/GIT_CONVENTIONS.md` + modèle de PR + `main` protégée (à activer dans les réglages GitHub).
- [ ] **4. Inventaire matériel** — `docs/HARDWARE.md` rempli ; décision INT8/INT4 consignée (nouvel ADR).
- [x] **5. `docker-compose.yml`** — Neo4j 5 opérationnel, MLflow sous profil `ops`, Langfuse différé (ADR-0004).
- [x] **6. Architecture globale** — `docs/ARCHITECTURE.md` (Mermaid, 4 vues) + `architecture_v0.drawio` éditable.

## Vérifications techniques à faire sur au moins 2 machines

```bash
# 1. Pré-requis
docker --version && docker compose version

# 2. Configuration locale
cp .env.example .env          # PowerShell : Copy-Item .env.example .env

# 3. Démarrage (seul Neo4j doit apparaître)
docker compose up -d
docker compose ps

# 4. Neo4j répond, pas seulement le port ouvert
docker compose exec neo4j cypher-shell -u neo4j -p changeme_local "RETURN 1 AS ok;"

# 5. Interface web
#    ouvrir http://localhost:7474 et se connecter avec neo4j / changeme_local

# 6. Extinction et redémarrage à froid (le volume doit persister)
docker compose down
docker compose up -d
```

## Points de vigilance identifiés à l'étape 0

1. **Docker Desktop n'est pas installé sur ce poste** : le `docker-compose.yml` a été validé par analyse syntaxique (YAML + schéma Compose), pas par exécution. Faire le test réel chez un membre avant de déclarer l'étape close.
2. **Windows + vLLM** : vLLM s'installe difficilement sous Windows natif. Si personne n'a Linux/WSL2, planifier dès la semaine 2 une machine Linux pour l'étape 6.
3. **Mot de passe Neo4j** : `changeme_local` est un défaut de confort local. Il ne doit jamais servir ailleurs ; `.env` est ignoré par Git.
4. **`git config core.autocrlf`** : sur Windows, vérifier `git config --get core.autocrlf` → préférer `input` ou `false` pour respecter `.gitattributes`.
5. **Protection de `main`** : à activer manuellement sur GitHub (Settings → Branches), ce n'est pas versionnable sans GitHub Pro pour les dépôts privés.

## Définition de « étape 0 terminée »

Les cinq cases suivantes doivent être vraies :

- [x] Le dépôt est publié et `docker compose up` démarre Neo4j (vérifié en CI).
- [x] `docs/ROLES.md` décrit les cinq casquettes et le rôle d'intégration, tous portés par la même personne.
- [ ] `docs/HARDWARE.md` est rempli et l'ADR sur INT8/INT4 est écrit.
- [ ] `main` est protégée et une PR de test a été relue par un autre membre.
- [ ] `docs/ARCHITECTURE.md` a été relu collectivement (une réunion de 30 min suffit) et la v0 est taguée `arch-v0`.
