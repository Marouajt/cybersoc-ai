"""Tests du perimetre fige a l'etape 1 (bloc A).

Deux niveaux :
  1. le perimetre reel du depot est coherent ;
  2. le validateur detecte reellement les derives (sinon il ne protege rien).

Le second point est le plus important : un validateur qu'on ne teste jamais
devient un decor qui valide tout.
"""

from __future__ import annotations

import copy

import pytest

from data.validate_scope import ACTIONS_ATTENDUES, charger, validate

SCOPE = charger()


def test_le_perimetre_du_depot_est_coherent() -> None:
    assert validate(SCOPE) == []


def test_entre_8_et_12_techniques_mitre() -> None:
    """La feuille de route borne le perimetre : au-dela, le benchmark se dilue."""
    assert 8 <= len(SCOPE["mitre_techniques"]) <= 12


def test_les_identifiants_mitre_sont_uniques() -> None:
    identifiants = [t["id"] for t in SCOPE["mitre_techniques"]]
    assert len(identifiants) == len(set(identifiants))


@pytest.mark.parametrize(
    "technique", SCOPE["mitre_techniques"], ids=[t["id"] for t in SCOPE["mitre_techniques"]]
)
def test_chaque_technique_a_un_jumeau_benin(technique: dict) -> None:
    """Regle structurante : sans jumeau benin, le jeu devient trivialement facile."""
    assert len(technique["benign_twin"].strip()) >= 20


def test_les_actions_correspondent_a_la_liste_fermee() -> None:
    identifiants = {item["id"] for item in SCOPE["actions"]["items"]}
    assert identifiants == ACTIONS_ATTENDUES


def test_le_split_se_fait_par_scenario() -> None:
    """Anti-fuite : un split par ligne laisserait un scenario a cheval sur train et test."""
    cibles = SCOPE["dataset_targets"]
    assert cibles["split_key"] == "scenario_id"
    assert abs(sum(cibles["split"].values()) - 1.0) < 1e-6


def test_la_part_de_cas_benins_respecte_la_fourchette() -> None:
    cibles = SCOPE["dataset_targets"]
    assert 0.4 <= cibles["benign_ratio_min"] <= cibles["benign_ratio_max"] <= 0.5


def test_le_controleur_de_domaine_est_declare_protege() -> None:
    """Condition du test de l'etape 8 : isoler SRV-DC-01 doit etre refuse."""
    proteges = {ressource["id"] for ressource in SCOPE["protected_resources"]}
    assert "SRV-DC-01" in proteges


# --- Le validateur doit savoir echouer ---------------------------------------


def _scope_modifie(mutation) -> dict:
    copie = copy.deepcopy(SCOPE)
    mutation(copie)
    return copie


@pytest.mark.parametrize(
    ("nom", "mutation", "message_attendu"),
    [
        (
            "jumeau benin supprime",
            lambda s: s["mitre_techniques"][0].update({"benign_twin": ""}),
            "jumeau benin",
        ),
        (
            "action hors liste fermee",
            lambda s: s["actions"]["items"][0].update({"id": "shutdown_dc"}),
            "liste fermee",
        ),
        (
            "split qui ne somme pas a 1",
            lambda s: s["dataset_targets"]["split"].update({"test": 0.4}),
            "somme",
        ),
        (
            "split par ligne au lieu du scenario",
            lambda s: s["dataset_targets"].update({"split_key": "case_id"}),
            "scenario_id",
        ),
        (
            "identifiant mitre en double",
            lambda s: s["mitre_techniques"][1].update({"id": s["mitre_techniques"][0]["id"]}),
            "double",
        ),
        (
            "actif protege retire",
            lambda s: s.update({"protected_resources": []}),
            "SRV-DC-01",
        ),
        (
            "trop de techniques",
            lambda s: s["mitre_techniques"].extend([copy.deepcopy(s["mitre_techniques"][0])] * 2),
            "attendu entre",
        ),
    ],
)
def test_le_validateur_refuse_une_derive(nom: str, mutation, message_attendu: str) -> None:
    erreurs = validate(_scope_modifie(mutation))
    assert erreurs, f"le validateur aurait du refuser : {nom}"
    assert any(message_attendu in erreur for erreur in erreurs), (
        f"message attendu contenant '{message_attendu}', obtenu : {erreurs}"
    )
