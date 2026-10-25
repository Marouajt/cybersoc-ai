"""Registre et telechargement des sources externes (etape 1, bloc B, tache 2).

Trois sources publiques, toutes productrices d'identifiants officiels :

  * MITRE ATT&CK (bundle STIX)  -> T#### / T####.###, G####, S####, C####
  * CISA KEV (catalogue JSON)   -> CVE exploitees dans la nature
  * MITRE CWE (catalogue XML)   -> CWE-###

Le telechargement est mis en cache dans `data/raw/` (non versionne) et chaque
fichier est identifie par son SHA-256 : sans cette empreinte, deux membres
pourraient produire des jeux differents en croyant utiliser "les memes donnees".
"""

from __future__ import annotations

import hashlib
import json
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
DOSSIER_RAW = RACINE / "data" / "raw"
DOSSIER_PROCESSED = RACINE / "data" / "processed"


@dataclass(frozen=True)
class Source:
    """Une source externe et ce qu'on en attend."""

    nom: str
    url: str
    fichier: str
    producteur: str
    usage: str
    licence: str
    licence_a_verifier: bool = True


SOURCES: tuple[Source, ...] = (
    Source(
        nom="mitre_attack_enterprise",
        url=(
            "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/"
            "master/enterprise-attack/enterprise-attack.json"
        ),
        fichier="enterprise-attack.json",
        producteur="MITRE",
        usage="techniques, tactiques, groupes, logiciels, campagnes",
        licence="MITRE ATT&CK Terms of Use (aucun fichier LICENSE dans le depot)",
    ),
    Source(
        nom="cisa_kev",
        url=(
            "https://www.cisa.gov/sites/default/files/feeds/"
            "known_exploited_vulnerabilities.json"
        ),
        fichier="known_exploited_vulnerabilities.json",
        producteur="CISA",
        usage="CVE reellement exploitees, avec produits et actions attendues",
        licence="publication officielle CISA (conditions a confirmer)",
    ),
    Source(
        nom="mitre_cwe",
        url="https://cwe.mitre.org/data/xml/cwec_latest.xml.zip",
        fichier="cwec_latest.xml.zip",
        producteur="MITRE",
        usage="faiblesses CWE, descriptions, mitigations, consequences",
        licence="CWE Terms of Use (a confirmer)",
    ),
)


def chemin_local(source: Source) -> Path:
    return DOSSIER_RAW / source.fichier


def empreinte_sha256(chemin: Path) -> str:
    """SHA-256 d'un fichier, lu par blocs (les bundles ATT&CK font > 50 Mo)."""
    digest = hashlib.sha256()
    with chemin.open("rb") as flux:
        for bloc in iter(lambda: flux.read(1024 * 1024), b""):
            digest.update(bloc)
    return digest.hexdigest()


def telecharger(source: Source, force: bool = False, timeout: int = 300) -> Path:
    """Telecharge la source si elle est absente (ou si `force`)."""
    destination = chemin_local(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not force:
        return destination

    requete = urllib.request.Request(
        source.url, headers={"User-Agent": "CyberSOC-AI/etape1 (+projet academique)"}
    )
    temporaire = destination.with_suffix(destination.suffix + ".part")
    with (
        urllib.request.urlopen(requete, timeout=timeout) as reponse,
        temporaire.open("wb") as sortie,
    ):
        for bloc in iter(lambda: reponse.read(1024 * 1024), b""):
            sortie.write(bloc)
    temporaire.replace(destination)
    return destination


def decrire(source: Source, nombre_enregistrements: int | None = None) -> dict:
    """Fiche de provenance pour le manifeste (versionnee, elle)."""
    chemin = chemin_local(source)
    fiche = asdict(source)
    fiche.update(
        {
            "fichier_local": str(chemin.relative_to(RACINE)).replace("\\", "/"),
            "octets": chemin.stat().st_size if chemin.exists() else None,
            "sha256": empreinte_sha256(chemin) if chemin.exists() else None,
            # Pas d'horodatage ici : le manifeste doit etre identique d'une
            # execution a l'autre, sinon `make data` salirait un fichier
            # versionne et le test « reconstruit a l'identique » serait faux.
            "enregistrements_normalises": nombre_enregistrements,
        }
    )
    return fiche


def ecrire_manifeste(fiches: list[dict], chemin: Path | None = None) -> Path:
    chemin = chemin or (DOSSIER_PROCESSED / "sources_manifest.json")
    chemin.parent.mkdir(parents=True, exist_ok=True)
    contenu = {
        "avertissement_licences": (
            "Les conditions d'utilisation des trois sources doivent etre "
            "confirmees dans DATASHEET.md (tache 12) avant toute publication."
        ),
        "sources": fiches,
    }
    chemin.write_text(
        json.dumps(contenu, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return chemin
