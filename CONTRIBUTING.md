# Contribuer

Règles complètes : [`docs/GIT_CONVENTIONS.md`](docs/GIT_CONVENTIONS.md).
Résumé opérationnel :

```bash
# 1. partir de main à jour
git switch main && git pull

# 2. une branche par tâche
git switch -c feat/1-normalisation-mitre

# 3. travailler, puis vérifier avant de committer
make check            # ou : python -m ruff check . && python -m pytest -q

# 4. un commit par tâche (message conventionnel)
git commit -am "feat(data): normaliser MITRE ATT&CK en JSONL"

# 5. pousser et ouvrir une PR relue par un autre membre
git push -u origin feat/1-normalisation-mitre
```

## Avant d'ouvrir une PR

- [ ] une seule tâche de la feuille de route par PR (numéro d'étape indiqué) ;
- [ ] `make check` passe ;
- [ ] aucune donnée lourde, aucun secret, aucun poids de modèle ajouté ;
- [ ] la section de README correspondante est mise à jour si l'étape en produit une ;
- [ ] les décisions structurantes sont consignées dans `docs/DECISIONS.md`.

## Style de code

- Python : `ruff` (règles E, F, W, I, UP, B, SIM), ligne max 100, typage explicite
  sur les frontières de module.
- Ne pas introduire de dépendance sans la déclarer dans `requirements.txt`, avec
  un commentaire indiquant l'étape concernée.
- Les scripts d'expérience peuvent être jetables ; les schémas Pydantic et les
  contrats d'API ne le sont jamais.

## Ce qui sera refusé en revue

1. Un résultat sans run MLflow ni configuration reproductible.
2. Un chiffre de performance mesuré une seule fois.
3. Une modification du jeu de test sans nouveau hash.
4. Une action exécutable sans validation ni approbation humaine.
5. Un `except: pass` masquant une erreur de parsing JSON du modèle.
