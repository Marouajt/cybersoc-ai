# `experiments/` — Expériences et résultats

**Rôle propriétaire** : responsable d'intégration, exécution par tous · **Étapes** : 2 à 12

Ce dossier contient **les scripts de comparaison et les résultats bruts**. Il ne
contient pas de code de production : un script d'expérience peut être jetable,
un résultat ne l'est jamais.

## Les 6 comparaisons imposées

| # | Comparaison | Étape | Ce qu'elle démontre |
|---|---|---|---|
| 1 | Qwen vs Phi | 2 | quel SLM convient à l'analyse cyber |
| 2 | Base vs Fine-tuné | 5 | apport du LoRA/QLoRA |
| 3 | No-RAG vs Vector vs Graph vs Hybrid | 3, 4 | apport du RAG et du graphe |
| 4 | FP16 vs INT8 vs INT4 | 6 | compromis mémoire / vitesse / qualité |
| 5 | Sans vs avec KV cache | 6 | effet du cache sur latence et débit |
| 6 | Single-Agent vs Multi-Agent | 7 | intérêt de l'architecture multi-agents |

## Structure des résultats

```
experiments/
├── runs/                  # un dossier par run : config.json, metrics.json, raw_predictions.jsonl
├── results/               # tableaux agrégés (CSV) prêts pour le rapport
├── figures/               # graphiques exportés (PNG/SVG) utilisés dans le rapport
├── scripts/               # un script par comparaison, appelé en boucle sur les configurations
└── mlruns/                # backend MLflow (NON versionné)
```

## Règles non négociables

1. **Chaque ligne d'un tableau du rapport doit pointer vers un run** (identifiant
   MLflow). Un chiffre sans run est un chiffre non reproductible, donc non recevable.
2. Toute mesure de performance est répétée **3 à 5 fois** ; on reporte moyenne et
   écart-type, jamais un seul tirage.
3. Le jeu de test ne change pas pendant une campagne : on vérifie le hash avant
   et après (`test.sha256`).
4. Les configurations sont déclaratives (fichier de config versionné), pas des
   arguments tapés à la main.
5. Aucune retouche manuelle d'un CSV de résultats : si le chiffre est faux, on
   corrige le script et on relance.

## Exemple de boucle de campagne

```python
for model in ["qwen", "phi"]:
    for rag in ["none", "vector", "graph", "hybrid"]:
        for quant in ["fp16", "int8", "int4"]:
            for rep in range(3):
                run_experiment(model=model, rag=rag, quant=quant, rep=rep)
```

## Critère de réussite de l'étape 12

Chaque conclusion du rapport est appuyée par **un chiffre et une explication**
(pourquoi ce résultat, quels compromis, quelles limites).
