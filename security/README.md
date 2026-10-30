# `security/` — Réponse contrôlée et sécurité du LLM

**Casquette** : Agents & sécurité · **Étapes** : 8 et 9

Ce module porte deux responsabilités distinctes : l'exécution sûre des actions
(étape 8) et la sécurité du LLM lui-même (étape 9).

## 1. Actions contrôlées (étape 8)

### Allowlist fermée

`isolate_host`, `block_ip`, `disable_user`, `reset_password`, `create_ticket`
(+ `no_action` comme valeur explicite).

### Schéma strict d'une action

| Champ | Rôle |
|---|---|
| `action_id` | identifiant unique (ex. `ACT-0042-1`) |
| `type` | doit appartenir à l'allowlist |
| `target` | doit exister dans le monde simulé |
| `justification` | texte court, appuyé sur des preuves |
| `risk` | low / medium / high |
| `evidence` | références aux chunks / nœuds du graphe utilisés |
| `reversible` | booléen |
| `status` | `PENDING` → `APPROVED` / `REJECTED` → `EXECUTED` / `FAILED` |

### Pipeline de validation

```
proposée → schéma valide ? → type autorisé ? → cible connue ? → ressource non protégée ?
        → PENDING (rien ne s'exécute) → approbation humaine → sandbox → journal
```

**Critère de réussite** : une action visant `SRV-DC-01` (contrôleur de domaine
marqué `protected`) est rejetée automatiquement, et aucune action ne s'exécute
sans approbation.

### Sandbox

Simulateur d'état : fausses machines, faux pare-feu, **aucune commande système
réelle**. L'état simulé est persistant (SQLite/PostgreSQL) pour que le journal
d'audit soit relisible et démontrable.

## 2. Sécurité du LLM (étape 9)

Méthode imposée : **attaquer → mesurer (ASR) → défendre → remesurer**, puis
mesurer les faux positifs et le surcoût de latence.

| Menace | Défense attendue |
|---|---|
| Prompt injection (directe) | délimiteurs, contenu déclaré non fiable, détecteur de motifs |
| Injection indirecte (documents, CTI piégée) | contenu récupéré jamais exécutable, nettoyage |
| Jailbreak | prompt système robuste, filtre d'entrée, refus vérifiés |
| Fuite de données | masquage secrets/PII, filtre de sortie |
| RAG poisoning | provenance, sources de confiance, validation avant indexation |
| Outils non sûrs | allowlist, validation d'entrées, sandbox |
| Agentivité excessive | moindre privilège, approbation humaine |
| Sorties non validées | schéma strict, vérification avant exécution |
| Auditabilité | journal complet : prompts, contexte, décisions, outils, actions |

## Arborescence

```
security/
├── actions.py          # schéma Pydantic + allowlist
├── validate.py         # moteur de validation
├── sandbox.py          # simulateur d'état, zéro effet réel
├── audit.py            # journalisation (SQLite/PostgreSQL)
├── attacks/            # jeux d'attaque par catégorie (50 à 100 par catégorie)
├── defenses/           # délimiteurs, détecteurs, filtres, masquage
└── evaluate.py         # ASR avant/après, faux positifs, latence
```

## Critère de réussite de l'étape 9

Baisse nette de l'ASR après défenses, avec un taux de faux positifs faible **et
documenté**. Un chiffre d'ASR sans jeu d'attaque versionné n'est pas recevable.
