# Manifeste des artefacts de modèles

Aucun poids de modèle n'est versionné dans Git (ADR-0007). Ce fichier est la
**seule source de vérité** pour reconstruire un artefact : sans une ligne
complète ici, un résultat du rapport n'est pas reproductible.

## Modèles de base

| Nom logique | Référence Hugging Face | Révision (commit) | Taille | Rôle |
|---|---|---|---|---|
| `qwen25-3b-instruct` | `Qwen/Qwen2.5-3B-Instruct` | à figer à l'étape 2 | ~3,1 Md | modèle principal |
| `phi35-mini-instruct` | `microsoft/Phi-3.5-mini-instruct` | à figer à l'étape 2 | ~3,8 Md | modèle comparé |

> Épingler la **révision** (hash de commit) et pas seulement le nom du modèle :
> un tag peut bouger, un hash non.

## Adaptateurs LoRA / QLoRA

| Nom | Modèle de base | Révision base | Données d'entraînement | Hyperparamètres | Hash de l'adaptateur | Run MLflow |
|---|---|---|---|---|---|---|
| _exemple_ | `qwen25-3b-instruct` | _hash_ | `data/benchmark/train.jsonl` (hash) | r=16, alpha=32, dropout=0.05, q_proj/v_proj | _sha256_ | _run_id_ |

## Modèles quantifiés

| Nom | Base | Méthode | Bits | Taille disque | F1 mesuré | Run de mesure |
|---|---|---|---|---|---|---|
| _exemple_ | `qwen25-3b-instruct` | AWQ | 4 | _Go_ | _valeur_ | _run_id_ |

## Commandes de reconstruction

```bash
# récupération du modèle de base épinglé
python -c "from huggingface_hub import snapshot_download; \
  snapshot_download('Qwen/Qwen2.5-3B-Instruct', revision='<commit>', local_dir='models/weights/qwen25-3b-instruct')"

# quantification (étape 6)
# voir models/quantize/ et le run MLflow associé
```

## Règles

1. Une ligne par artefact réellement produit, jamais de ligne « prévue ».
2. Le hash de l'adaptateur est calculé sur le fichier `adapter_model.safetensors`.
3. Tout artefact utilisé dans un tableau du rapport doit référencer un run MLflow.
4. Les poids se téléchargent via `HF_HOME` défini dans `.env` (jamais dans Git).
