# `kg/` — Knowledge Graph Neo4j

**Rôle propriétaire** : M2 (Knowledge Graph) · **Étape** : 4

## Contrat d'interface

| Entrée | Sortie |
|---|---|
| `data/processed/mitre.jsonl`, `cve.jsonl`, `cwe.jsonl` | base Neo4j peuplée |
| entités extraites des alertes (`data/`) | requêtes Cypher réutilisables + sous-graphe sérialisé en texte |

## Schéma cible (v0)

**Nœuds** : `User`, `Host`, `IP`, `Alert`, `CVE`, `CWE`, `Malware`, `Technique`, `Tactic`

**Relations** : `LOGGED_INTO`, `CONNECTED_TO`, `TRIGGERED`, `EXPLOITS`, `USES`,
`HAS_WEAKNESS`, `PART_OF`

```
(User)-[:LOGGED_INTO]->(Host)-[:CONNECTED_TO]->(IP)
(Alert)-[:ON]->(Host)
(Alert)-[:TRIGGERED]->(Technique)
(Technique)-[:PART_OF]->(Tactic)
(Malware)-[:USES]->(Technique)
(CVE)-[:EXPLOITS]->(CWE)
```

## Arborescence

```
kg/
├── schema.cypher        # contraintes et index (idempotent, exécutable plusieurs fois)
├── import_mitre.py      # STIX → nœuds/relations
├── import_cve_cwe.py
├── import_alerts.py     # entités extraites des alertes
├── queries/             # requêtes Cypher nommées et testées
│   ├── neighborhood.cypher
│   ├── alert_to_technique.cypher
│   └── hosts_by_malware.cypher
├── neo4j_data/          # volume Docker (NON versionné)
└── neo4j_import/        # dépôt CSV pour LOAD CSV (NON versionné)
```

## Requêtes de référence

Voisinage d'une IP, chemin d'une alerte vers sa technique, hôtes touchés par un
malware : ces trois requêtes sont exigées par la feuille de route et servent de
tests de non-régression du graphe.

```cypher
MATCH (a:Alert {id:$alert_id})-[:ON]->(h:Host)<-[:LOGGED_INTO]-(u:User)
OPTIONAL MATCH (a)-[:TRIGGERED]->(t:Technique)
RETURN h.name AS host, u.name AS user, t.id AS technique;
```

## Critère de réussite de l'étape 4

**Chaque entité présente dans les alertes de test existe dans le graphe.** Cette
vérification est un test automatisé, pas une inspection visuelle : elle évite le
piège « entités synthétiques absentes du graphe » signalé pour l'étape 1.

## Connexion

```
bolt://localhost:7687   (docker compose up)
Neo4j Browser : http://localhost:7474
identifiants : voir .env (NEO4J_USER / NEO4J_PASSWORD)
```
