# `docs/` — Documentation du projet

| Fichier | Contenu | Propriétaire |
|---|---|---|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | architecture v0, séquence du fil rouge, portée des modules | responsable d'intégration |
| [`ROLES.md`](ROLES.md) | 5 rôles, matrice RACI, interfaces figées, signatures | responsable d'intégration |
| [`GIT_CONVENTIONS.md`](GIT_CONVENTIONS.md) | branches, commits, PR, fichiers interdits dans Git | responsable d'intégration |
| [`HARDWARE.md`](HARDWARE.md) | inventaire du matériel, matrice INT8/INT4 | M3 |
| [`PLANNING.md`](PLANNING.md) | calendrier, jalons, chemin critique, risques | responsable d'intégration |
| [`DECISIONS.md`](DECISIONS.md) | journal des décisions (ADR-0001 à 0007) | tous (une entrée par décision) |
| [`CHECKLIST_ETAPE0.md`](CHECKLIST_ETAPE0.md) | checklist de l'étape 0 | responsable d'intégration |
| [`architecture/`](architecture/) | sources du schéma : `.mmd` (Mermaid) et `.drawio` (éditable) | responsable d'intégration |

## Règle de tenue

La documentation se met à jour **dans la PR de l'étape concernée**. Un document
qui décrit une décision non encore appliquée doit porter une mention explicite
(« à rédiger à l'étape N ») pour éviter de faire croire que le travail est fait.

Les ADR ne sont jamais supprimés : une décision remplacée est archivée et
référencée par l'ADR qui la remplace. C'est ce qui rendra crédible la section
« discussion » du rapport final.
