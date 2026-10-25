"""Validation du perimetre du projet (data/scope.json).

Ce module ne valide pas des donnees : il valide le CONTRAT passe entre les
5 membres a l'etape 1 (bloc A). Il est volontairement en bibliotheque standard
uniquement, pour tourner partout sans installation.

Usage :
    python -m data.validate_scope            # verifie data/scope.json
    python -m data.validate_scope chemin.json

Sortie : un code retour 0 si le perimetre est coherent, 1 sinon, avec la liste
des anomalies. Les tests de tests/test_scope.py s'appuient sur validate().
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

SCOPE_PATH = Path(__file__).with_name("scope.json")

TECHNIQUE_ID = re.compile(r"^T\d{4}(\.\d{3})?$")

TACTIQUES = {
    "reconnaissance",
    "resource-development",
    "initial-access",
    "execution",
    "persistence",
    "privilege-escalation",
    "defense-evasion",
    "credential-access",
    "discovery",
    "lateral-movement",
    "collection",
    "command-and-control",
    "exfiltration",
    "impact",
}

# Liste fermee imposee par la feuille de route (etape 8).
ACTIONS_ATTENDUES = {
    "isolate_host",
    "block_ip",
    "disable_user",
    "reset_password",
    "create_ticket",
    "no_action",
}

TARGET_KINDS = {"host", "external_ip", "user", "none"}
RISQUES = {"none", "low", "medium", "high"}
SEVERITES_ATTENDUES = ["low", "medium", "high", "critical"]
DIFFICULTES_ATTENDUES = {"easy", "medium", "hard"}

CLES_OBLIGATOIRES = [
    "document",
    "scope_version",
    "project",
    "roadmap_step",
    "status",
    "random_seed",
    "changelog",
    "mitre_techniques",
    "alert_types",
    "telemetry_sources",
    "actions",
    "severities",
    "difficulty_levels",
    "protected_resources",
    "world",
    "dataset_targets",
    "case_rules",
    "out_of_scope",
]


def charger(chemin: Path = SCOPE_PATH) -> dict[str, Any]:
    """Charge le perimetre depuis le disque."""
    with chemin.open(encoding="utf-8") as flux:
        return json.load(flux)


def _champs(objet: dict[str, Any], requis: list[str], prefixe: str, erreurs: list[str]) -> None:
    for champ in requis:
        valeur = objet.get(champ)
        if valeur is None or (isinstance(valeur, str) and not valeur.strip()):
            erreurs.append(f"{prefixe} : champ obligatoire manquant ou vide -> '{champ}'")


def _valider_techniques(scope: dict[str, Any], erreurs: list[str]) -> None:
    techniques = scope.get("mitre_techniques") or []
    minimum, maximum = (scope.get("consistency_checks") or {}).get("techniques_count_range", [8, 12])

    if not minimum <= len(techniques) <= maximum:
        erreurs.append(
            f"mitre_techniques : {len(techniques)} techniques, attendu entre {minimum} et {maximum}"
        )

    vus: set[str] = set()
    types_alertes = {t.get("id") for t in scope.get("alert_types") or []}

    for index, technique in enumerate(techniques):
        prefixe = f"mitre_techniques[{index}]"
        identifiant = technique.get("id", "")
        prefixe = f"mitre_techniques[{index}] ({identifiant or 'sans id'})"

        _champs(technique, ["id", "name", "tactic", "why", "benign_twin", "alert_types"], prefixe, erreurs)

        if not TECHNIQUE_ID.match(identifiant or ""):
            erreurs.append(f"{prefixe} : identifiant MITRE invalide -> '{identifiant}'")
        if identifiant in vus:
            erreurs.append(f"{prefixe} : identifiant en double")
        vus.add(identifiant)

        if technique.get("tactic") not in TACTIQUES:
            erreurs.append(f"{prefixe} : tactique inconnue -> '{technique.get('tactic')}'")

        # Regle structurante : chaque technique malveillante a un jumeau benin.
        jumeau = (technique.get("benign_twin") or "").strip()
        if len(jumeau) < 20:
            erreurs.append(f"{prefixe} : jumeau benin absent ou trop vague (min. 20 caracteres)")

        references = technique.get("alert_types") or []
        if not references:
            erreurs.append(f"{prefixe} : aucune alerte associee")
        for reference in references:
            if reference not in types_alertes:
                erreurs.append(f"{prefixe} : type d'alerte non defini -> '{reference}'")

        parent = technique.get("parent")
        if parent is not None and not TECHNIQUE_ID.match(parent):
            erreurs.append(f"{prefixe} : identifiant parent invalide -> '{parent}'")
        if parent and not identifiant.startswith(f"{parent}."):
            erreurs.append(f"{prefixe} : parent '{parent}' incoherent avec l'identifiant")


def _valider_types_alertes(scope: dict[str, Any], erreurs: list[str]) -> None:
    telemetrie = {
        cle for cle in (scope.get("telemetry_sources") or {}) if not cle.startswith("note")
    }
    vus: set[str] = set()

    for index, alerte in enumerate(scope.get("alert_types") or []):
        prefixe = f"alert_types[{index}] ({alerte.get('id') or 'sans id'})"
        _champs(alerte, ["id", "label", "description", "telemetry"], prefixe, erreurs)

        if alerte.get("id") in vus:
            erreurs.append(f"{prefixe} : identifiant en double")
        vus.add(alerte.get("id"))

        for source in alerte.get("telemetry") or []:
            if source not in telemetrie:
                erreurs.append(f"{prefixe} : source de telemetrie non declaree -> '{source}'")

    if not vus:
        erreurs.append("alert_types : aucun type d'alerte defini")


def _valider_actions(scope: dict[str, Any], erreurs: list[str]) -> None:
    items = (scope.get("actions") or {}).get("items") or []
    identifiants = [item.get("id") for item in items]

    if set(identifiants) != ACTIONS_ATTENDUES:
        manquantes = ACTIONS_ATTENDUES - set(identifiants)
        en_trop = set(identifiants) - ACTIONS_ATTENDUES
        if manquantes:
            erreurs.append(f"actions : actions imposees manquantes -> {sorted(manquantes)}")
        if en_trop:
            erreurs.append(f"actions : actions hors liste fermee -> {sorted(en_trop)}")
    if len(identifiants) != len(set(identifiants)):
        erreurs.append("actions : identifiants en double")

    for index, item in enumerate(items):
        prefixe = f"actions[{index}] ({item.get('id') or 'sans id'})"
        _champs(item, ["id", "target_kind", "reversible", "risk", "description"], prefixe, erreurs)
        if item.get("target_kind") not in TARGET_KINDS:
            erreurs.append(f"{prefixe} : target_kind invalide -> '{item.get('target_kind')}'")
        if item.get("risk") not in RISQUES:
            erreurs.append(f"{prefixe} : risque invalide -> '{item.get('risk')}'")
        if not isinstance(item.get("reversible"), bool):
            erreurs.append(f"{prefixe} : 'reversible' doit etre un booleen")


def _valider_severites(scope: dict[str, Any], erreurs: list[str]) -> None:
    severites = scope.get("severities") or []
    identifiants = [s.get("id") for s in severites]

    if identifiants != SEVERITES_ATTENDUES:
        erreurs.append(
            f"severities : attendu {SEVERITES_ATTENDUES} dans cet ordre, obtenu {identifiants}"
        )

    rangs = [s.get("rank") for s in severites]
    if rangs != list(range(1, len(severites) + 1)):
        erreurs.append(f"severities : rangs attendus 1..{len(severites)}, obtenu {rangs}")

    for index, severite in enumerate(severites):
        prefixe = f"severities[{index}] ({severite.get('id')})"
        _champs(severite, ["id", "rank", "description", "examples"], prefixe, erreurs)
        if not severite.get("examples"):
            erreurs.append(f"{prefixe} : au moins un exemple est attendu")

    difficultes = {d.get("id") for d in scope.get("difficulty_levels") or []}
    if difficultes != DIFFICULTES_ATTENDUES:
        erreurs.append(
            f"difficulty_levels : attendu {sorted(DIFFICULTES_ATTENDUES)}, obtenu {sorted(difficultes)}"
        )


def _valider_cibles(scope: dict[str, Any], erreurs: list[str]) -> None:
    cibles = scope.get("dataset_targets") or {}

    obligatoires = [
        "cases_min",
        "cases_max",
        "cases_target",
        "benign_ratio_min",
        "benign_ratio_max",
        "real_cases_min",
        "real_cases_max",
        "double_annotated_cases",
        "cohen_kappa_min",
        "retrieval_qa_min",
        "retrieval_qa_max",
        "split",
        "split_key",
    ]
    deja_signalees = len(erreurs)
    _champs(cibles, obligatoires, "dataset_targets", erreurs)
    if len(erreurs) > deja_signalees:
        # ne pas enchainer des comparaisons sur des champs absents
        return

    if cibles["cases_min"] > cibles["cases_target"] > cibles["cases_max"]:
        erreurs.append("dataset_targets : cases_min <= cases_target <= cases_max non respecte")

    if not 0 < cibles["benign_ratio_min"] <= cibles["benign_ratio_max"] < 1:
        erreurs.append("dataset_targets : la part de cas benins doit etre dans l'intervalle ]0, 1[")
    if cibles["benign_ratio_min"] < 0.4 or cibles["benign_ratio_max"] > 0.5:
        erreurs.append(
            "dataset_targets : la feuille de route impose 40 a 50 % de cas benins"
        )

    if not 0 <= cibles["cohen_kappa_min"] <= 1:
        erreurs.append("dataset_targets : cohen_kappa_min doit etre dans [0, 1]")

    split = cibles["split"]
    total = sum(split.get(cle, 0) for cle in ("train", "validation", "test"))
    if abs(total - 1.0) > 1e-6:
        erreurs.append(f"dataset_targets.split : la somme vaut {total}, attendu 1.0")
    if not 0.5 <= split.get("train", 0) < 1:
        erreurs.append("dataset_targets.split : la part d'entrainement doit etre majoritaire")

    if cibles["split_key"] != "scenario_id":
        erreurs.append(
            "dataset_targets.split_key : le split doit se faire par 'scenario_id' (anti-fuite)"
        )


def _valider_etat(scope: dict[str, Any], erreurs: list[str]) -> None:
    statut = scope.get("status")
    if statut not in {"proposed", "validated"}:
        erreurs.append(f"status : valeur invalide -> '{statut}'")
    if statut == "validated" and not scope.get("frozen_at"):
        erreurs.append("status='validated' exige une date 'frozen_at'")

    journal = scope.get("changelog") or []
    if not journal:
        erreurs.append("changelog : au moins une entree est requise")
    elif journal[-1].get("version") != scope.get("scope_version"):
        erreurs.append(
            "changelog : la derniere entree doit porter la version courante "
            f"'{scope.get('scope_version')}'"
        )

    if not isinstance(scope.get("random_seed"), int):
        erreurs.append("random_seed : un entier est requis (reproductibilite)")

    proteges = {c.get("id") for c in scope.get("protected_resources") or []}
    attendu = (scope.get("consistency_checks") or {}).get("protected_host_present", "SRV-DC-01")
    if attendu not in proteges:
        erreurs.append(f"protected_resources : l'actif protege '{attendu}' doit etre declare")


def validate(scope: dict[str, Any]) -> list[str]:
    """Retourne la liste des incoherences du perimetre (vide si tout est valide)."""
    erreurs: list[str] = []

    _champs(scope, CLES_OBLIGATOIRES, "scope", erreurs)
    if erreurs:
        return erreurs

    _valider_techniques(scope, erreurs)
    _valider_types_alertes(scope, erreurs)
    _valider_actions(scope, erreurs)
    _valider_severites(scope, erreurs)
    _valider_cibles(scope, erreurs)
    _valider_etat(scope, erreurs)

    if not scope.get("case_rules"):
        erreurs.append("case_rules : les regles de construction des cas sont obligatoires")
    if not scope.get("out_of_scope"):
        erreurs.append("out_of_scope : lister ce qui est exclu est obligatoire")

    return erreurs


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    chemin = Path(argv[0]) if argv else SCOPE_PATH

    try:
        scope = charger(chemin)
    except FileNotFoundError:
        print(f"ERREUR : fichier introuvable -> {chemin}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"ERREUR : JSON invalide dans {chemin} -> {exc}", file=sys.stderr)
        return 1

    erreurs = validate(scope)
    if erreurs:
        print(f"PERIMETRE INVALIDE ({len(erreurs)} anomalie(s)) :", file=sys.stderr)
        for erreur in erreurs:
            print(f"  - {erreur}", file=sys.stderr)
        return 1

    techniques = len(scope["mitre_techniques"])
    actions = len(scope["actions"]["items"])
    print(
        f"Perimetre valide : {scope['scope_version']} ({scope['status']}), "
        f"{techniques} techniques MITRE, {actions} actions, "
        f"{len(scope['alert_types'])} types d'alertes, "
        f"{len(scope['severities'])} niveaux de severite."
    )
    if scope["status"] != "validated":
        print("Rappel : statut 'proposed' -> le bloc A n'est clos qu'apres signature des 5 membres.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
