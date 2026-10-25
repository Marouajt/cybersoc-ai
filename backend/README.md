# `backend/` — API FastAPI

**Rôle propriétaire** : M5 (Web & LLMOps) · **Étape** : 11

## Contrat d'API (cible, étape 11)

| Méthode | Route | Rôle |
|---|---|---|
| `POST` | `/alerts` | ingestion d'une alerte normalisée, déclenche le triage |
| `GET` | `/incidents` | liste des incidents avec priorité et statut |
| `POST` | `/investigate/{id}` | lance l'enquête, **streaming SSE** des étapes de l'agent |
| `GET` | `/graph/{id}` | sous-graphe de l'incident, format compatible react-force-graph |
| `POST` | `/actions/{id}/approve` | approbation humaine d'une action |
| `POST` | `/actions/{id}/reject` | rejet, avec motif obligatoire |
| `GET` | `/audit` | journal d'audit filtrable |
| `GET` | `/health` | sonde de disponibilité (utilisée par la CI et Docker) |

## Principes

1. **L'API ne contient aucune logique d'IA** : elle appelle `agents/` et `security/`.
2. **Le streaming SSE est obligatoire** pour `/investigate/{id}` : une enquête de
   plusieurs secondes doit montrer sa progression, pas un spinner.
3. **Aucune action ne s'exécute sur un `GET`** : tout effet de bord est un `POST`
   explicite et tracé.
4. **Pydantic pour tout** : requêtes, réponses, erreurs. Une réponse non conforme
   au schéma est un bug, pas une tolérance.
5. L'approbation est **idempotente** : deux clics ne produisent pas deux exécutions.

## Arborescence

```
backend/
├── main.py          # application FastAPI, montage des routeurs
├── routers/         # alerts, incidents, investigate, graph, actions, audit
├── schemas.py       # contrats d'API (réexporte les schémas de data/ et security/)
├── store.py         # persistance (SQLite en local, PostgreSQL en cible)
├── sse.py           # streaming des étapes d'investigation
└── tests/           # tests d'API (TestClient)
```

## Critère de réussite de l'étape 11

Le parcours complet — alerte, enquête, approbation, exécution sandbox, audit —
fonctionne dans l'interface, lancée par `docker compose up`.
