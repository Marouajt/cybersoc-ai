## Tâche traitée

Étape de la feuille de route : **étape N — …**
Case de la checklist concernée : <!-- ex. étape 1, tâche 5 -->

## Ce que fait cette PR

<!-- 2 à 4 lignes. Pourquoi, pas comment. -->

## Comment vérifier

```bash
# commandes exactes permettant au relecteur de reproduire
```

## Checklist

- [ ] Une seule tâche de la feuille de route dans cette PR
- [ ] `make check` (ruff + pytest) passe localement
- [ ] Un commit par tâche (rebase interactif si nécessaire)
- [ ] Aucun secret, poids de modèle ou donnée lourde ajouté
- [ ] Section de README correspondante mise à jour (si l'étape en produit une)
- [ ] Décision structurante consignée dans `docs/DECISIONS.md` (si applicable)
- [ ] Si un jeu de test a changé : nouveau hash SHA-256 + entrée DATASHEET

## Impact sur les autres modules

<!-- Quels contrats d'interface changent ? Qui doit être prévenu ? -->

## Relecture

- [ ] Relue et approuvée par un autre membre que l'auteur : @
