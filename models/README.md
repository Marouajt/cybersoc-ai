# `models/` — SLM, fine-tuning, optimisation d'inférence

**Casquette** : Modèles & optimisation · **Étapes** : 2, 5, 6

## Contrat d'interface

| Entrée | Sortie |
|---|---|
| `data/benchmark/test.jsonl` (figé, hashé) | tableau comparatif Qwen / Phi (`experiments/`) |
| `data/benchmark/train.jsonl` | adaptateur LoRA versionné + manifeste |
| configuration matérielle (`docs/HARDWARE.md`) | serveur LLM compatible OpenAI (`POST /v1/chat/completions`) consommé par la casquette Agents & sécurité |

Le serveur exposé à l'étape 6 est **l'interface critique** : l'étape 7 (agents)
ne doit jamais importer `transformers` directement, seulement appeler l'endpoint.

## Arborescence

```
models/
├── benchmark/          # script unique d'évaluation (prompt fixe, température 0, JSON imposé)
├── finetune/           # conversion au format instruction, LoRA / QLoRA
├── quantize/           # FP16, INT8, INT4 (bitsandbytes, AWQ, GPTQ, GGUF)
├── serving/            # vLLM, variantes de configuration
├── weights/            # NON versionné (.gitignore)
├── adapters/           # adaptateurs LoRA (poids ignorés, config + hash versionnés)
└── MANIFEST.md         # modèle de base, révision HF, hash, hyperparamètres, commande
```

## Règles de mesure

1. **Un seul script d'évaluation** pour tous les modèles, prompt identique, `temperature=0`, sortie JSON imposée. Un chiffre produit par un autre chemin n'est pas comparable.
2. Toujours mesurer et stocker : accuracy, précision, rappel, F1, taux d'hallucination, TTFT, tokens/s, mémoire GPU/RAM.
3. **Hallucination** = ID MITRE ou CVE absent des listes valides de `data/processed/`. C'est une mesure objective, pas une appréciation.
4. Répéter les mesures de performance **3 à 5 fois**, reporter moyenne **et** écart-type.
5. Toute mesure est accompagnée du GPU, de la version de CUDA/PyTorch et de la graine : un chiffre sans métadonnées est refusé en revue.
6. Le modèle de base se compare au modèle fine-tuné **avec le même protocole et le même jeu de test figé**.

## Pièges connus

- comparer deux modèles sur deux machines différentes ;
- oublier de vider le cache GPU entre deux mesures (`torch.cuda.empty_cache()` + `reset_peak_memory_stats`) ;
- mesurer le TTFT sans préciser la longueur de prompt ;
- conclure sur un gain de fine-tuning sans vérifier l'absence de fuite train/test.
