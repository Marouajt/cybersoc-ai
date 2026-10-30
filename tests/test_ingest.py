"""Tests du bloc B : decoupage et artefacts produits.

Deux familles :
  * tests unitaires du chunking, sur des textes synthetiques (toujours executes) ;
  * tests d'integration sur les fichiers versionnes de `data/processed/`,
    qui verifient la coherence entre le manifeste, les listes et les chunks.

Les tests d'integration ne dependent pas des 55 Mo de sources brutes : ils
tournent donc en CI sans telechargement.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

from data.build_all import cle_naturelle
from data.chunking import (
    CIBLE_TOKENS,
    MAX_TOKENS,
    construire_chunks,
    decouper,
    estimer_tokens,
    statistiques,
)

RACINE = Path(__file__).resolve().parents[1]
PROCESSED = RACINE / "data" / "processed"
CHUNKS = PROCESSED / "chunks.jsonl"
TEXTE_LONG = " ".join(
    f"La phrase numero {i} decrit un comportement observable sur un poste de travail."
    for i in range(80)
)


def lire_jsonl(chemin: Path) -> list[dict]:
    with chemin.open(encoding="utf-8") as flux:
        return [json.loads(ligne) for ligne in flux if ligne.strip()]


# --- chunking ------------------------------------------------------------

def test_estimation_tokens_coherente():
    assert estimer_tokens("") == 1
    assert estimer_tokens("abcd") == 1
    assert estimer_tokens("a" * 4000) == 1000


def test_texte_court_reste_en_un_chunk():
    morceaux = decouper("Une seule phrase courte sur une alerte.")
    assert len(morceaux) == 1


def test_texte_long_decoupe_et_borne():
    morceaux = decouper(TEXTE_LONG)
    assert len(morceaux) > 1
    assert all(estimer_tokens(m) <= MAX_TOKENS for m in morceaux)
    # le decoupage doit viser la cible, pas produire des miettes
    assert max(estimer_tokens(m) for m in morceaux) >= CIBLE_TOKENS // 2


def test_chevauchement_effectif_entre_morceaux_consecutifs():
    morceaux = decouper(TEXTE_LONG)
    premier = set(morceaux[0].split(". "))
    second = set(morceaux[1].split(". "))
    assert premier & second, "les chunks consecutifs doivent partager du texte"


def test_phrase_geant_sans_ponctuation_ne_boucle_pas():
    geant = "mot " * 5000
    morceaux = decouper(geant)
    assert len(morceaux) > 1
    assert all(estimer_tokens(m) <= MAX_TOKENS for m in morceaux)


def test_chunks_deterministes_et_identifiants_stables():
    donnees = {
        "techniques": [
            {
                "mitre_id": "T9999",
                "nom": "Technique de test",
                "tactiques": ["execution"],
                "description": "Description suffisamment longue pour un chunk.",
                "sous_technique": False,
                "parent": None,
                "plateformes": ["Windows"],
                "url": None,
                "revoque": False,
                "obsolete": False,
            }
        ]
    }
    premier = construire_chunks(donnees)
    second = construire_chunks(donnees)
    assert premier == second
    assert premier[0]["chunk_id"] == "mitre:T9999#0"
    assert premier[0]["meta"]["mitre_id"] == "T9999"


def test_objet_obsolete_exclu_du_corpus():
    base = {
        "mitre_id": "T9998",
        "nom": "Obsolete",
        "tactiques": [],
        "description": "Texte.",
        "sous_technique": False,
        "parent": None,
        "plateformes": [],
        "url": None,
        "revoque": False,
    }
    chunks = construire_chunks({"techniques": [dict(base, obsolete=True)]})
    assert chunks == []


# --- artefacts versionnes ------------------------------------------------

exige_artefacts = pytest.mark.skipif(
    not (PROCESSED / "mitre_ids.txt").exists(),
    reason="data/processed absent : lancer `python -m data.build_all --offline`",
)
exige_chunks = pytest.mark.skipif(
    not CHUNKS.exists(),
    reason="corpus dÃ©rivÃ© absent : lancer `python -m data.build_all --offline`",
)


@exige_artefacts
def test_artefacts_presents_et_non_vides():
    for nom in (
        "mitre_techniques.jsonl",
        "kev_cves.jsonl",
        "cwe_faiblesses.jsonl",
        "mitre_ids.txt",
        "cve_ids.txt",
        "cwe_ids.txt",
        "sources_manifest.json",
    ):
        chemin = PROCESSED / nom
        assert chemin.exists(), f"{nom} manquant"
        assert chemin.stat().st_size > 0, f"{nom} vide"


@exige_artefacts
def test_manifeste_coherent_avec_les_fichiers():
    manifeste = json.loads(
        (PROCESSED / "sources_manifest.json").read_text(encoding="utf-8")
    )
    attendus = manifeste["enregistrements"]
    for nom_fichier, cle in (
        ("mitre_techniques.jsonl", "mitre_techniques"),
        ("kev_cves.jsonl", "kev_cves"),
        ("cwe_faiblesses.jsonl", "cwe_faiblesses"),
        ("mitre_groupes.jsonl", "mitre_groupes"),
    ):
        assert len(lire_jsonl(PROCESSED / nom_fichier)) == attendus[cle]
    for nom, fiche in manifeste["listes_identifiants"].items():
        assert (PROCESSED / f"{nom}_ids.txt").exists()
        assert fiche["entrees"] > 0


@exige_artefacts
def test_manifeste_decrit_le_corpus_derive():
    """Le corpus chunké n'est pas versionné : le manifeste doit le déclarer."""
    manifeste = json.loads(
        (PROCESSED / "sources_manifest.json").read_text(encoding="utf-8")
    )
    chunks = manifeste["chunks"]
    assert chunks["versionne"] is False
    assert len(chunks["sha256"]) == 64
    assert chunks["total_chunks"] > 1000
    assert chunks["regenerer_avec"].startswith("python -m data.build_all")


@exige_chunks
def test_corpus_derive_identique_au_manifeste():
    """Si le corpus est présent, il doit correspondre à l'empreinte publiée."""
    manifeste = json.loads(
        (PROCESSED / "sources_manifest.json").read_text(encoding="utf-8")
    )
    empreinte = hashlib.sha256(CHUNKS.read_bytes()).hexdigest()
    assert empreinte == manifeste["chunks"]["sha256"], (
        "le corpus ne correspond plus au manifeste : relancer `make data`"
    )


@exige_artefacts
def test_listes_identifiants_triees_et_uniques():
    for nom, motif in (
        ("mitre_ids", r"^[TGSC]\d{4}(\.\d{3})?$"),
        ("cve_ids", r"^CVE-\d{4}-\d{4,}$"),
        ("cwe_ids", r"^CWE-\d+$"),
    ):
        valeurs = (PROCESSED / f"{nom}.txt").read_text(encoding="utf-8").split()
        assert len(valeurs) == len(set(valeurs)), f"{nom} : doublons"
        assert valeurs == sorted(set(valeurs), key=cle_naturelle), f"{nom} : non trie"
        assert all(re.match(motif, v) for v in valeurs), f"{nom} : format inattendu"


@exige_artefacts
def test_perimetre_du_projet_existe_dans_attck():
    """Les 11 techniques de scope.json doivent exister dans le referentiel officiel."""
    identifiants = set(
        (PROCESSED / "mitre_ids.txt").read_text(encoding="utf-8").split()
    )
    perimetre = json.loads((RACINE / "data" / "scope.json").read_text(encoding="utf-8"))
    absentes = [
        technique["id"]
        for technique in perimetre["mitre_techniques"]
        if technique["id"] not in identifiants
    ]
    assert absentes == [], f"techniques inventees dans scope.json : {absentes}"


@exige_chunks
def test_chunks_valides_et_tracables():
    chunks = lire_jsonl(CHUNKS)
    assert len(chunks) > 1000
    identifiants = {c["chunk_id"] for c in chunks}
    assert len(identifiants) == len(chunks), "chunk_id duplique"

    prefixes = {"technique": "mitre:", "cve": "cve:", "cwe": "cwe:"}
    for chunk in chunks:
        assert 0 < chunk["tokens"] <= MAX_TOKENS
        assert chunk["tokenizer"] == "approx_chars_div_4"
        assert chunk["texte"].strip()
        attendu = prefixes.get(chunk["doc_type"], "mitre:")
        assert chunk["doc_id"].startswith(attendu)


@exige_chunks
def test_texte_des_chunks_est_nettoye():
    """Aucun artefact web ne doit subsister dans le corpus indexe."""
    echantillon = lire_jsonl(CHUNKS)[:800]
    for chunk in echantillon:
        assert "(Citation:" not in chunk["texte"]
        assert not re.search(r"\]\(https?://", chunk["texte"])


@exige_chunks
def test_statistiques_coherentes_avec_les_chunks():
    chunks = lire_jsonl(CHUNKS)
    stats = statistiques(chunks)
    assert stats["total_chunks"] == len(chunks)
    assert stats["chunks_superieurs_500"] == 0
    assert 0 < stats["tokens_moyen"] <= MAX_TOKENS
    assert sum(stats["par_type"].values()) == len(chunks)
