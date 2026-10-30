# Périmètre figé du projet (étape 1, bloc A)

> **Statut : `proposed` — 0.1.0-draft.** Le bloc A n'est clos qu'après la revue
> en trois passes (§ 11). Tant que le statut vaut `proposed`, aucun jeu de données
> ne doit être généré en masse : une modification du périmètre après coup
> obligerait à tout régénérer.
>
> Source de vérité machine : [`data/scope.json`](../data/scope.json).
> Vérification : `python -m data.validate_scope` (code retour 0 = cohérent).

## 1. À quoi sert ce document

Le périmètre répond à quatre questions, et à elles seules :

1. **Quelles attaques** le système doit-il savoir reconnaître ? → 11 techniques MITRE.
2. **Quels signaux** les alertes contiennent-elles ? → 9 types d'alertes + télémétrie.
3. **Quelles réponses** sont autorisées ? → liste fermée de 6 actions.
4. **Quelles gradations** de gravité et de difficulté ? → 4 sévérités, 3 difficultés.

Il ne définit **pas** les schémas de données (`Alert`, `BenchmarkCase`) : c'est la
tâche 4 du bloc C. Le périmètre fixe les *valeurs*, les schémas fixent la *forme*.

## 2. Les 11 techniques retenues

La feuille de route en impose 8 à 12. Onze techniques couvrent la chaîne
d'attaque de bout en bout sans diluer le benchmark : chaque étape du kill chain
a au moins une technique, et chaque technique a un **jumeau bénin** (règle du
bloc D, anticipée ici pour éviter d'annoter plus tard des cas impossibles à
équilibrer).

| # | ID | Technique | Tactique | Jumeau bénin (résumé) |
|---|----|-----------|----------|------------------------|
| 1 | T1566.001 | Spearphishing Attachment | initial-access | pièce jointe d'un fournisseur connu, macros désactivées |
| 2 | T1204.002 | Malicious File | execution | `.xlsm` avec macro signée et approuvée |
| 3 | T1059.001 | PowerShell | execution | script signé d'un admin depuis le VPN |
| 4 | T1027 | Obfuscated Files or Information | defense-evasion | script encodé par Intune/SCCM depuis un hôte de management |
| 5 | T1078 | Valid Accounts | initial-access | compte de service après rotation de mot de passe planifiée |
| 6 | T1053.005 | Scheduled Task | persistence | tâche de mise à jour d'un installateur signé |
| 7 | T1003.001 | LSASS Memory | credential-access | agent EDR signé en allowlist |
| 8 | T1021.001 | Remote Desktop Protocol | lateral-movement | session RDP d'admin depuis un jump host |
| 9 | T1041 | Exfiltration Over C2 Channel | exfiltration | sauvegarde planifiée vers un domaine approuvé |
| 10 | T1105 | Ingress Tool Transfer | command-and-control | mise à jour applicative depuis un CDN approuvé |
| 11 | T1486 | Data Encrypted for Impact | impact | archive protégée par mot de passe créée par un utilisateur |

### Couverture du kill chain

| Phase | Techniques présentes |
|---|---|
| Accès initial | T1566.001, T1078 |
| Exécution | T1204.002, T1059.001 |
| Persistance | T1053.005 |
| Élévation / évasion | T1027 |
| Accès aux identifiants | T1003.001 |
| Mouvement latéral | T1021.001 |
| Command & control | T1105 |
| Exfiltration | T1041 |
| Impact | T1486 |

### Pourquoi ces trois-là en plus des 8 imposées

Les 8 techniques citées en exemple par la feuille de route (T1566, T1078,
T1059.001, T1053.005, T1003.001, T1021.001, T1041, T1486) ne permettent pas de
distinguer « fichier ouvert » de « code exécuté », ni de traiter l'obfuscation
séparément de l'exécution. D'où :

- **T1204.002** : isole l'action de l'utilisateur, indispensable pour que le
  jumeau bénin de T1566.001 soit crédible ;
- **T1027** : `powershell -enc` est le marqueur du fil rouge ; sans cette
  technique, l'encodage serait confondu avec la malveillance elle-même ;
- **T1105** : donne au jeu un signal réseau entrant (téléchargement d'outil),
  là où T1041 ne couvre que le sortant.

### Point de vigilance sur les noms

Les libellés ci-dessus sont ceux d'ATT&CK Enterprise à notre connaissance. Ils
seront **confirmés automatiquement** à la tâche 3, quand le bundle STIX officiel
sera téléchargé et que `data/processed/mitre_ids.txt` sera généré : un ID absent
de cette liste est une erreur de périmètre, pas une hallucination du modèle.
Ne pas générer de données avant cette confirmation.

## 3. Les 9 types d'alertes

| ID | Libellé | Télémétrie |
|---|---|---|
| `process_creation` | Création de processus | Security 4688, Sysmon 1 |
| `office_child_process` | Processus enfant d'Office | Security 4688 |
| `encoded_command` | Commande encodée / obfusquée | Security 4688, Sysmon 1 |
| `failed_logon_burst` | Rafale d'échecs d'authentification | Security 4625 |
| `anomalous_logon` | Connexion anormale (horaire, RDP, hôte inédit) | Security 4624, 4672 |
| `scheduled_task_created` | Création de tâche planifiée | Security 4698, Sysmon 1 |
| `lsass_access` | Accès mémoire à `lsass` | Sysmon 10 |
| `external_connection` | Connexion sortante vers l'extérieur | Sysmon 3, proxy |
| `mass_file_modification` | Modification massive de fichiers | Sysmon 11, Security 4663 |

Chaque alerte est normalisée vers le schéma `Alert` ; l'événement brut reste
dans le champ `raw`. **Périmètre Windows uniquement** (voir § 7).

## 4. Les 6 actions autorisées

Liste **fermée** : toute action hors de ce tableau doit être rejetée par le
moteur de validation de l'étape 8, et un modèle qui en propose une est compté
comme une sortie invalide.

| Action | Cible | Réversible | Risque | Garde-fou |
|---|---|---|---|---|
| `isolate_host` | hôte | oui | medium | refusée si l'actif est protégé (`SRV-DC-01`) |
| `block_ip` | IP externe | oui | low | refusée si IP interne ou plage réservée |
| `disable_user` | utilisateur | oui | high | refusée si compte de service critique |
| `reset_password` | utilisateur | oui | medium | ne remplace pas une désactivation si compromission active |
| `create_ticket` | aucune | oui | low | — |
| `no_action` | aucune | oui | none | à utiliser pour un cas bénin confirmé |

Une seule action attendue par cas (`expected_action` + `expected_target`).

## 5. Sévérités et difficultés

| Sévérité | Rang | Critère | Exemple |
|---|---|---|---|
| `low` | 1 | anomalie d'hygiène, aucun indicateur d'attaque | échec de connexion isolé |
| `medium` | 2 | indicateur suspect isolé, non corrélé | commande encodée sans destination externe |
| `high` | 3 | outil offensif confirmé, ou deux signaux indépendants corrélés | Office lance PowerShell encodé |
| `critical` | 4 | impact actif ou actif critique compromis | chiffrement en cours, mouvement vers SRV-DC-01 |

Difficultés : `easy` (signal unique explicite), `medium` (signal explicite mais
contexte ambigu, ou deux signaux faibles), `hard` (indistinguable du légitime
sans connaissance du contexte).

## 6. Monde simulé et cibles du jeu de données

| Élément | Valeur |
|---|---|
| Utilisateurs / hôtes | ~40 / ~40 |
| Nommage | `WKS-<DEPT>-<NN>`, `SRV-<ROLE>-<NN>` (FIN, RH, IT, MKT, OPS) |
| Réseau interne | `10.10.0.0/16` |
| Actif protégé | `SRV-DC-01` (contrôleur de domaine) |
| Graine | `RANDOM_SEED=42` |

**Convention sur les IP externes :** les cas synthétiques utilisent les plages
de documentation TEST-NET (`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`)
pour ne désigner aucune infrastructure réelle. L'IP `185.220.101.4` du fil rouge
ALR-0042 reste une illustration, pas une donnée du jeu.

| Cible | Valeur |
|---|---|
| Cas annotés | 250 à 500 (cible 400) |
| Part de bénins | 40 à 50 % |
| Cas réels (`origin`) | 50 à 100 |
| Double annotation | 50 cas, kappa > 0,8 |
| Questions de retrieval | 100 à 200 |
| Split | 60 / 15 / 25, **par `scenario_id`** |
| Chunks | 300 à 500 tokens, 10 à 15 % de chevauchement |

## 7. Hors périmètre (explicite)

| Exclu | Raison |
|---|---|
| Cloud (Azure, AWS, GCP), conteneurs, Kubernetes | télémétrie et topologie différentes ; on garde un périmètre Windows homogène |
| Postes Linux et macOS | un seul modèle de journaux pour rester comparable |
| OT / ICS | hors du périmètre d'un SOC bureautique |
| Mobile | aucun journal équivalent |
| Vishing, attaques physiques | non observables dans la télémétrie retenue |
| Supply chain (T1195) | nécessite des artefacts de build absents du monde simulé |
| Exfiltration physique / impression | non détectable dans les journaux choisis |
| Exécution réelle d'une action | tout est simulé en sandbox, jamais appliqué |
| Plus de 12 techniques | au-delà, le benchmark se dilue |

## 8. Règles de construction des cas (rappel)

1. Chaque scénario malveillant a un **jumeau bénin**.
2. Un cas = une alerte = une action et une cible attendues.
3. `scenario_id` obligatoire, partagé par tous les cas du même scénario.
4. Aucune donnée personnelle réelle (Faker, domaines internes fictifs).
5. Toute entité citée existe dans le monde simulé, donc dans le graphe (étape 4).
6. Tout ID MITRE/CVE/CWE cité appartient aux listes valides.

## 9. Comment vérifier

```bash
python -m data.validate_scope          # cohérence du périmètre
python -m pytest tests/test_scope.py   # 25 tests, y compris les dérives volontaires
```

Le validateur refuse notamment : un jumeau bénin absent, une action hors liste
fermée, un split qui ne somme pas à 1, un `split_key` différent de
`scenario_id`, un identifiant MITRE en double, un actif protégé manquant.

## 10. Politique de modification

Toute modification **après** validation :

1. incrémente `scope_version` et ajoute une entrée au `changelog` ;
2. invalide le benchmark existant (il faudra régénérer et re-hasher) ;
3. exige un commit dédié et daté (jamais une modification opportuniste glissée dans un autre travail) ;
4. est signalée dans `DATASHEET.md` et dans la section « limites » du rapport.

## 11. Revue et gel du périmètre (projet individuel)

La feuille de route prévoyait une validation par les 5 membres. Le projet étant
mené **seul**, cette procédure est remplacée par une revue en trois passes :
même fonction (ne pas figer un périmètre qu'on n'a pas relu), preuve différente
(des dates et un tag Git plutôt que des signatures).

### Passe 1 — cohérence interne (30 min)

- [ ] chaque technique a un **jumeau bénin que je saurais reconnaître sans le modèle** ;
- [ ] chaque type d'alerte est relié à au moins une technique ;
- [ ] chaque action a une cible compatible (`host`, `ip`, `user`) ;
- [ ] les 6 actions couvrent les réponses que ce périmètre peut exiger ;
- [ ] aucun cas du périmètre n'exige une action absente de la liste ;
- [ ] les 4 sévérités sont distinguables sur un exemple concret chacune.

### Passe 2 — vérification factuelle (10 min)

- [ ] `python -m data.validate_scope` passe sans erreur ;
- [ ] les 11 identifiants existent dans le référentiel officiel (`pytest tests/test_ingest.py::test_perimetre_du_projet_existe_dans_attck`) ;
- [ ] les libellés ATT&CK correspondent bien aux identifiants (pas d'ID juste avec le mauvais nom).

### Passe 3 — faisabilité (20 min)

- [ ] je sais produire un cas bénin crédible pour **chaque** technique ;
- [ ] je sais produire un cas malveillant pour **chaque** technique ;
- [ ] aucune technique ne dépend d'une télémétrie que je ne sais pas simuler ;
- [ ] le volume visé (250–500 cas) reste atteignable avec le temps disponible.

### Gel

Une fois les trois passes faites, dans cet ordre :

1. `status` → `"validated"`, `frozen_at` → date du jour, `scope_version` → `1.0.0` ;
2. `python -m data.validate_scope` (le validateur exige une date dès que le statut vaut `validated`) ;
3. `git tag -a scope-v1.0.0 -m "périmètre gelé"` puis push du tag.

Le tag est la preuve horodatée que le périmètre a été figé **avant** les
expériences — plus solide qu'une signature, puisqu'il est vérifiable par
n'importe qui.

| Passe | Date | Verdict | Remarques |
|---|---|---|---|
| 1 — cohérence interne | | ☐ conforme ☐ à corriger | |
| 2 — vérification factuelle | | ☐ conforme ☐ à corriger | |
| 3 — faisabilité | | ☐ conforme ☐ à corriger | |

*Avis de l'encadrant (facultatif mais recommandé) :* date ……………… — ☐ favorable ☐ réserves

## 12. Journal

| Version | Date | Changement |
|---|---|---|
| 0.1.0-draft | 2026-10-25 | proposition initiale : 11 techniques, 9 types d'alertes, 6 actions, 4 sévérités |
