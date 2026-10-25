"""Tests transverses de cohérence du dépôt (étape 0).

Ces tests ne vérifient pas du code métier : ils garantissent que le squelette
sur lequel les 5 membres vont travailler reste intact — arborescence imposée,
contrats documentés, service Neo4j déclaré, secrets non versionnés.

Ils servent aussi de filet de sécurité en revue de PR : une PR qui casse la
structure ou le docker-compose échoue en CI, pas en réunion.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).resolve().parents[1]

DOSSIERS_IMPOSES = [
    "data",
    "models",
    "rag",
    "kg",
    "agents",
    "security",
    "backend",
    "frontend",
    "experiments",
    "docs",
]

DOCUMENTS_ATTENDUS = [
    "README.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "docs/ARCHITECTURE.md",
    "docs/ROLES.md",
    "docs/GIT_CONVENTIONS.md",
    "docs/HARDWARE.md",
    "docs/PLANNING.md",
    "docs/DECISIONS.md",
    "docs/CHECKLIST_ETAPE0.md",
    "docs/architecture/architecture_v0.mmd",
    "docs/architecture/architecture_v0.drawio",
]


def _compose() -> dict:
    with (RACINE / "docker-compose.yml").open(encoding="utf-8") as flux:
        return yaml.safe_load(flux)


@pytest.mark.parametrize("dossier", DOSSIERS_IMPOSES)
def test_dossier_impose_existe_et_documente(dossier: str) -> None:
    """Chaque module imposé existe et expose son contrat dans un README."""
    chemin = RACINE / dossier
    assert chemin.is_dir(), f"dossier manquant : {dossier}/"
    assert (chemin / "README.md").is_file(), f"contrat manquant : {dossier}/README.md"


@pytest.mark.parametrize("document", DOCUMENTS_ATTENDUS)
def test_document_attendu_existe(document: str) -> None:
    assert (RACINE / document).is_file(), f"document manquant : {document}"


def test_compose_declare_neo4j_avec_les_ports_attendus() -> None:
    services = _compose()["services"]
    assert "neo4j" in services, "le service neo4j doit être déclaré"

    neo4j = services["neo4j"]
    assert neo4j["image"].startswith("neo4j:5"), "image Neo4j 5 attendue"
    assert "7474:7474" in neo4j["ports"], "port HTTP 7474 attendu"
    assert "7687:7687" in neo4j["ports"], "port Bolt 7687 attendu"
    assert "healthcheck" in neo4j, "un healthcheck est requis pour valider le démarrage"
    assert neo4j["environment"]["NEO4J_AUTH"], "NEO4J_AUTH doit être configuré"


def test_compose_ne_demarre_que_neo4j_par_defaut() -> None:
    """Critère de l'étape 0 : `docker compose up` ne doit lancer que Neo4j.

    Tout service d'observabilité doit rester derrière un profil (ADR-0002),
    sinon les machines modestes de l'équipe ne démarrent pas.
    """
    services = _compose()["services"]
    sans_profil = {
        nom
        for nom, definition in services.items()
        if not definition.get("profiles")
    }
    assert sans_profil == {"neo4j"}, f"services démarrés par défaut : {sorted(sans_profil)}"


def test_modele_env_documente_les_variables_critiques() -> None:
    contenu = (RACINE / ".env.example").read_text(encoding="utf-8")
    for variable in ["NEO4J_USER", "NEO4J_PASSWORD", "NEO4J_URI", "RANDOM_SEED"]:
        assert variable in contenu, f"variable non documentée dans .env.example : {variable}"


def test_env_reel_n_est_pas_versionne() -> None:
    """`.env` peut exister localement, mais il doit être ignoré par Git."""
    regles = (RACINE / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".env" in regles, ".env doit figurer dans .gitignore"


def test_aucun_poids_de_modele_versionne() -> None:
    """Aucun fichier de poids ne doit traîner dans le dépôt (ADR-0007)."""
    extensions_interdites = {".safetensors", ".gguf", ".bin", ".pt", ".onnx"}
    fautifs = [
        chemin.relative_to(RACINE).as_posix()
        for chemin in RACINE.rglob("*")
        if chemin.is_file() and chemin.suffix in extensions_interdites
    ]
    assert not fautifs, f"poids de modèle trouvés dans le dépôt : {fautifs}"


def test_roles_et_signature_presents() -> None:
    """Le document de rôles doit contenir les 5 rôles et le rôle d'intégration."""
    contenu = (RACINE / "docs/ROLES.md").read_text(encoding="utf-8")
    for intitule in [
        "Données & RAG",
        "Knowledge Graph",
        "Modèles & optimisation",
        "Agents & sécurité",
        "Web & LLMOps",
        "Responsable d'intégration",
    ]:
        assert intitule in contenu, f"rôle absent de docs/ROLES.md : {intitule}"
