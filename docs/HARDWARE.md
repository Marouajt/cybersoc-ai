# Inventaire du matériel de calcul

> **Statut : à compléter avant la fin de la semaine 1.**
> Ce document décide de deux choses : la taille maximale des SLM et le choix
> INT8 ou INT4 (étapes 2 et 6). Tant qu'il est vide, il faut supposer le
> pire cas (pas de GPU local) et travailler sur Colab/Kaggle.

## 1. La machine

Une seule machine porte les cinq casquettes : c'est la contrainte dimensionnante
du projet, car il n'existe aucune machine de repli si elle est occupée ou tombe
en panne.

| Machine | CPU / RAM | GPU + VRAM | CUDA / pilote | Dispo GPU (h/semaine) | Colab | Kaggle | Serveur université |
|---|---|---|---|---|---|---|---|
| | | | | | ☐ | ☐ | ☐ |

Commandes utiles pour remplir la ligne GPU :

```bash
# NVIDIA (Windows ou Linux)
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv

# macOS (Apple Silicon : Metal, pas CUDA)
system_profiler SPDisplaysDataType | grep -i "chipset\|vram"

# RAM et CPU
# Windows PowerShell : Get-CimInstance Win32_ComputerSystem | Select TotalPhysicalMemory
# Linux : free -h && lscpu | head -20
```

## 2. Besoin mémoire des modèles pressentis

Ordres de grandeur, poids seuls, hors activations et hors cache KV
(les valeurs exactes seront mesurées à l'étape 6, pas supposées) :

| Modèle | Paramètres | FP16 | INT8 | INT4 |
|---|---|---|---|---|
| Qwen2.5-3B-Instruct | ~3,1 Md | ~6,2 Go | ~3,1 Go | ~1,6–1,9 Go |
| Phi-3.5-mini-instruct | ~3,8 Md | ~7,6 Go | ~3,8 Go | ~2,0–2,3 Go |

Règle de sécurité : prévoir **+2 à +3 Go** pour le cache KV (contexte 4k) et les
activations, et viser **≤ 80 % de la VRAM disponible**.

## 3. Matrice de décision

| VRAM disponible | Ce qui est réaliste | Conséquence sur le projet |
|---|---|---|
| **Aucun GPU** (CPU seul) | SLM ≤ 1,5 Md en INT4 via llama.cpp, ou API distante pour la partie qualitative | Étape 2 limitée à 1–2 modèles ; étapes 5 et 6 réduites (mesures CPU uniquement) ; le rapport doit le dire explicitement |
| **4–6 Go** | 3B en INT4, Phi-3.5-mini en INT4 | INT4 obligatoire, batch = 1 ; fine-tuning QLoRA très lent → privilégier Colab |
| **8 Go** | 3B en INT4/INT8, fine-tuning QLoRA possible sur 1–2 epochs | configuration la plus probable ; FP16 réservé au CPU offload |
| **12–16 Go** | 3B en FP16, 3,8B en INT8, QLoRA confortable | toutes les comparaisons FP16/INT8/INT4 réalisables |
| **24 Go+** | 7B en INT4, batching confortable, vLLM avec plusieurs séquences | on peut ajouter un 3e modèle (Qwen2.5-7B) au benchmark |

## 4. Plateformes de repli

| Plateforme | Atout | Limite à noter dans le rapport |
|---|---|---|
| Colab (Free / Pro) | GPU T4 ou L4, setup instantané | sessions interrompues, quotas, résultats à re-télécharger |
| Kaggle | 2× T4 16 Go, 30 h/semaine | quota hebdomadaire, pas de service long |
| Serveur universitaire | GPU dédié, jobs longs | file d'attente, accès à planifier |
| vLLM en local | indispensable pour l'étape 6 (batching, prefix caching) | Linux/WSL2 recommandé, support Windows limité |

**Point de vigilance étape 6 :** vLLM s'installe difficilement sous Windows
natif. Si aucun membre n'a Linux/WSL2, prévoir dès la semaine 2 une machine
Linux (serveur universitaire ou VM cloud) pour les mesures de serving.

## 5. Contrainte de reproductibilité

Le matériel doit être identique pour comparer deux modèles (étape 2) ou deux
quantifications (étape 6). Toute mesure doit donc être accompagnée de :
modèle de GPU, VRAM, version de CUDA, version de PyTorch, et du `RANDOM_SEED`.
Un tableau de résultats sans ces métadonnées sera refusé en revue.
