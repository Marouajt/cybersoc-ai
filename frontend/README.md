# `frontend/` — Interface analyste (React + TypeScript)

**Rôle propriétaire** : M5 (Web & LLMOps) · **Étape** : 11

## Écrans attendus

| Écran | Contenu |
|---|---|
| **Incidents** | liste triable, priorité, statut, sévérité, temps écoulé |
| **Détail d'incident** | alerte brute, explication IA, score de risque, techniques MITRE, CVE/CWE liés |
| **Investigation** | progression en direct (SSE), étapes de l'agent, sources RAG utilisées |
| **Graphe** | exploration du voisinage (react-force-graph ou Cytoscape.js) |
| **Approbation** | action proposée, preuves, risque, réversibilité, boutons Approuver / Rejeter |
| **Audit** | journal complet, filtrable par incident et par type d'action |
| **Monitoring** (optionnel) | latence, taux de rejet humain, hallucinations |

## Principes

1. **Commencer simple et complet de bout en bout**, le design vient après : un
   parcours fonctionnel laid vaut mieux qu'un beau mockup non branché.
2. **Aucune clé ni secret dans le front** : tout passe par le backend.
3. **L'action dangereuse est visuellement distincte** : l'approbation d'un
   `isolate_host` ne doit pas ressembler à un bouton « OK » neutre.
4. Multilinguisme FR/AR possible plus tard, mais **non requis par le sujet** :
   ne pas investir de temps dessus tant que le parcours n'est pas complet.

## Arborescence

```
frontend/
├── src/
│   ├── pages/       # Incidents, IncidentDetail, Graph, Audit
│   ├── components/  # action panel, risk badge, timeline
│   ├── api/         # client typé (fetch + types générés depuis OpenAPI)
│   └── hooks/       # useSSE, useIncidents
├── index.html
└── vite.config.ts
```

## Conventions

- TypeScript strict ; pas de `any` non justifié.
- Les types d'API sont dérivés du schéma OpenAPI de FastAPI, pas dupliqués à la main.
- Variables d'environnement Vite : uniquement `VITE_API_BASE_URL`.
