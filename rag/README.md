# `rag/` — Vector-RAG, Graph-RAG, Hybrid RAG

**Rôles propriétaires** : M1 (vectoriel) et M2 (graphe) · **Étapes** : 3 et 4

## Contrat d'interface

Une seule fonction publique, utilisée par les agents (étape 7) et par les
expériences (étape 12) :

```python
def retrieve(alert: Alert, mode: Literal["none", "vector", "graph", "hybrid"], k: int = 5) -> Context:
    """Retourne un contexte prêt à être injecté dans le prompt, avec sa provenance."""
```

`Context` contient au minimum : `text`, `chunks` (source, id, score), `mode`,
`k`, et les identifiants récupérés (MITRE, CVE, CWE). La provenance est
obligatoire : elle sert à la détection de *RAG poisoning* (étape 9).

## Les quatre modes comparés

| Mode | Mécanisme | Question à laquelle il répond |
|---|---|---|
| `none` | aucun contexte | baseline de référence |
| `vector` | top-k par similarité (embeddings) | « quels documents ressemblent à cette alerte ? » |
| `graph` | entités de l'alerte → sous-graphe Neo4j → texte structuré | « quelles relations relient ces entités ? » |
| `hybrid` | fusion des deux listes par Reciprocal Rank Fusion | « les deux signaux concordent-ils ? » |

RRF : `score(d) = Σ 1 / (60 + rang_i(d))` sur chaque liste de résultats.

## Arborescence

```
rag/
├── base.py         # interface retrieve() + type Context
├── chunking.py     # découpage 300–500 tokens, chevauchement 10–15 %
├── embed.py        # modèle d'embeddings (à figer à l'étape 3)
├── vector_store.py # indexation + requête (Chroma pressenti)
├── graph_rag.py    # extraction d'entités → Cypher → sérialisation en texte
├── hybrid.py       # RRF, déduplication
└── evaluate.py     # Recall@k, MRR, précision du contexte
```

## Règles

1. Les quatre modes tournent avec **le même script** d'évaluation, sur le **même** `retrieval_qa.jsonl`.
2. Métriques minimales : Recall@k, MRR, et pour k ∈ {3, 5, 10}.
3. Le chunking est un paramètre d'expérience, pas une constante cachée : taille et chevauchement sont tracés dans le run MLflow.
4. Aucun contenu récupéré n'est exécuté comme instruction. Le texte récupéré est toujours délimité et déclaré non fiable (défense contre l'injection indirecte, étape 9).

## Décisions ouvertes

- modèle d'embeddings (BGE / E5 / GTE / MiniLM) → étape 3, après mesure ;
- Chroma vs FAISS vs Qdrant → étape 3 ;
- re-ranking → optionnel, seulement si le Recall@k plafonne.
