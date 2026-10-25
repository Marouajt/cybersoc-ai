# Journal des décisions (ADR)

Chaque décision structurante est datée, motivée et réversible. Une décision
changée n'est jamais effacée : on la marque « remplacée par ADR-xxxx » pour que
le rapport puisse expliquer *pourquoi* le système a évolué.

Format : `ADR-NNNN — titre` · statut (proposé / accepté / remplacé) · contexte ·
décision · conséquences.

---

## ADR-0001 — Monorepo avec les 10 dossiers imposés

- **Date** : 2026-10-25 · **Statut** : accepté
- **Contexte** : cinq personnes, dix modules, un seul livrable GitHub noté.
- **Décision** : un dépôt unique, arborescence exacte `data/ models/ rag/ kg/ agents/ security/ backend/ frontend/ experiments/ docs/`, chaque module avec son `README.md` décrivant son contrat d'entrée/sortie. Un `tests/` et un `.github/` sont ajoutés (non imposés mais nécessaires à la CI).
- **Conséquences** : intégration simple, historique unique pour le rapport ; en contrepartie, risque de conflits sur les fichiers partagés (`docker-compose.yml`, schémas Pydantic, `docs/DECISIONS.md`). Mitigation : ces fichiers sont déclarés « à forte contention » dans `docs/GIT_CONVENTIONS.md`.

## ADR-0002 — Docker Compose avec profil `ops`

- **Date** : 2026-10-25 · **Statut** : accepté
- **Contexte** : le critère de l'étape 0 exige `docker compose up` fonctionnel chez les cinq membres, dont certains ont une machine modeste. MLflow et Langfuse ne servent qu'à l'étape 10.
- **Décision** : `docker compose up` ne démarre que Neo4j. MLflow est déclaré sous `profiles: ["ops"]`, donc lancé uniquement via `docker compose --profile ops up`. Langfuse est laissé hors du fichier (sa stack officielle est lourde : Postgres, ClickHouse, Redis, MinIO).
- **Conséquences** : démarrage rapide et robuste partout ; l'observabilité est opt-in. Un membre qui n'a jamais lancé le profil `ops` ne peut pas reproduire les figures de l'étape 10 → le README doit le préciser.

## ADR-0003 — Neo4j 5 sans plugin au démarrage

- **Date** : 2026-10-25 · **Statut** : accepté
- **Contexte** : le tag `neo4j:5` est celui de la feuille de route. L'activation d'APOC (`NEO4J_PLUGINS`) télécharge un plugin au premier démarrage : sans réseau, le conteneur échoue et le critère de l'étape 0 tombe.
- **Décision** : v0 sans plugin ; la ligne est présente en commentaire dans `docker-compose.yml` pour être activée à l'étape 4 si les procédures APOC deviennent nécessaires. Mémoire bornée à 1 Go de heap + 512 Mo de page cache pour tenir sur 16 Go de RAM.
- **Conséquences** : démarrage fiable ; à l'étape 4, décider explicitement si APOC est requis (import CSV en masse, par exemple) et le cas échéant documenter l'exigence réseau.

## ADR-0004 — Langfuse différé à l'étape 10

- **Date** : 2026-10-25 · **Statut** : proposé (à confirmer à l'étape 10)
- **Contexte** : deux options d'observabilité LLM sont citées par la feuille de route (Langfuse ou LangSmith). Langfuse est auto-hébergeable mais multi-services ; LangSmith est un SaaS.
- **Décision** : ne rien trancher maintenant. MLflow couvre les runs et les métriques dès l'étape 2 (local, gratuit, suffisant). Le traçage des trajectoires d'agents sera réévalué à l'étape 7-10, quand le volume de traces sera connu.
- **Conséquences** : `.env.example` réserve déjà `LANGFUSE_*` ; aucune dépendance n'est imposée à l'équipe avant d'en avoir besoin.

## ADR-0005 — `scenario_id` obligatoire dès le schéma initial

- **Date** : 2026-10-25 · **Statut** : accepté
- **Contexte** : la feuille de route impose un split train/validation/test **par scénario**, pas par ligne. Ajouter ce champ après coup obligerait à réannoter ou à re-générer tout le benchmark.
- **Décision** : `scenario_id` est un champ obligatoire, non nul, du schéma `BenchmarkCase` (étape 1), et le split se fait par `GroupShuffleSplit(groups=scenario_id)`.
- **Conséquences** : aucun scénario ne peut être coupé entre deux splits ; en contrepartie, les proportions 60/15/25 sont approximatives (elles s'appliquent à des groupes, pas à des lignes). Cette approximation doit être documentée dans `DATASHEET.md`.

## ADR-0006 — Un commit par tâche, fusion en rebase

- **Date** : 2026-10-25 · **Statut** : accepté
- **Contexte** : la règle « un commit par tâche » est explicite dans le sujet ; le squash-merge produirait un commit par PR (équivalent) mais casserait la correspondance tâche ↔ commit si une PR couvre plusieurs tâches.
- **Décision** : une branche = une tâche, une PR = un commit (rebase interactif avant revue si nécessaire), fusion en **rebase and merge**. `main` est protégée, revue par un autre membre obligatoire.
- **Conséquences** : historique linéaire et lisible, utilisé directement dans le rapport pour montrer la contribution de chacun.

## ADR-0007 — Aucun poids de modèle dans Git

- **Date** : 2026-10-25 · **Statut** : accepté
- **Contexte** : les adaptateurs LoRA et les modèles quantifiés pèsent de quelques dizaines de Mo à plusieurs Go.
- **Décision** : `.gitignore` exclut `*.safetensors`, `*.gguf`, `*.bin`, `*.pt`. `models/MANIFEST.md` documente pour chaque artefact : modèle de base, révision Hugging Face, hash, paramètres d'entraînement, commande de reproduction. DVC reste optionnel.
- **Conséquences** : dépôt léger et clonable ; la reproductibilité repose sur le manifeste, qui doit donc être tenu à jour à chaque étape 5 et 6.
