"""Point d'entrée de la reconstruction complète des données (`make data`).

Squelette créé à l'étape 0 pour que `make data` échoue avec un message utile
plutôt qu'avec un `ModuleNotFoundError`. L'implémentation réelle appartient à
l'étape 1 : collecte MITRE / CISA KEV / CWE / CTI, normalisation JSONL,
monde simulé, scénarios synthétiques, benchmark annoté, splits par scénario.
"""

from __future__ import annotations

import sys

MESSAGE = """\
`make data` n'est pas encore implémenté : c'est le livrable de l'étape 1.

À produire ici (voir data/README.md) :
  1. scope.json           périmètre figé (8 à 12 techniques MITRE, actions, sévérités)
  2. schemas.py           Alert, BenchmarkCase, RetrievalQA (Pydantic v2)
  3. collecte + normalisation -> data/processed/*.jsonl + listes d'IDs valides
  4. monde simulé         ~40 utilisateurs, hôtes, IP internes, SRV-DC-01 protégé
  5. benchmark annoté     train / val / test par scenario_id + test.sha256
  6. retrieval_qa.jsonl   100 à 200 questions-réponses de retrieval
  7. DATASHEET.md         sources, licences, méthode, répartition, limites

Reproductibilité : la graine vient de RANDOM_SEED (voir .env.example).
"""


def main() -> int:
    print(MESSAGE, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
