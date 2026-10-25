"""Normalisation des sources brutes en enregistrements JSONL (bloc B, tache 3).

Regle de conception : on conserve l'identifiant officiel de chaque objet
(`T1059.001`, `CVE-2021-44228`, `CWE-79`) comme cle primaire. C'est lui qui
servira, a l'etape 2, a prouver qu'un modele hallucine : un identifiant cite
qui n'existe pas dans ces listes est un identifiant invente.
"""

from __future__ import annotations

import io
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS_CWE = {"c": "http://cwe.mitre.org/cwe-7"}
ESPACES = re.compile(r"[ \t\u00a0]+")
SAUTS = re.compile(r"\n{3,}")
CITATION = re.compile(r"\s*\(Citation:[^)]*\)")
LIEN_MARKDOWN = re.compile(r"\[([^\]]+)\]\([^)]+\)")


def nettoyer(texte: str | None) -> str:
    """Compacte les espaces sans perdre les paragraphes."""
    if not texte:
        return ""
    texte = texte.replace("\r\n", "\n").replace("\r", "\n")
    texte = ESPACES.sub(" ", texte)
    texte = SAUTS.sub("\n\n", texte)
    return texte.strip()


def nettoyer_attack(texte: str | None) -> str:
    """Nettoie une description ATT&CK destinee au RAG.

    Les bundles STIX sont ecrits pour un site web : ils contiennent des appels
    de citation `(Citation: ...)` et des liens Markdown. Ces artefacts n'ont
    aucune valeur pour la recherche vectorielle et polluent les embeddings, on
    les retire en gardant le texte des liens.
    """
    texte = nettoyer(texte)
    texte = LIEN_MARKDOWN.sub(r"\1", texte)
    texte = CITATION.sub("", texte)
    return ESPACES.sub(" ", texte).strip()


def _identifiant_attack(objet: dict) -> str | None:
    for reference in objet.get("external_references", []) or []:
        if reference.get("source_name") == "mitre-attack":
            identifiant = reference.get("external_id")
            if identifiant:
                return identifiant
    return None


def _url_attack(objet: dict) -> str | None:
    for reference in objet.get("external_references", []) or []:
        if reference.get("source_name") == "mitre-attack":
            return reference.get("url")
    return None


def charger_bundle_attack(chemin: Path) -> dict:
    with chemin.open(encoding="utf-8") as flux:
        bundle = json.load(flux)
    objets = bundle.get("objects", [])
    return {"bundle": bundle, "objets": objets}


def _tactiques(objet: dict) -> list[str]:
    return [
        phase["phase_name"]
        for phase in objet.get("kill_chain_phases", []) or []
        if phase.get("kill_chain_name") == "mitre-attack"
    ]


def normaliser_mitre(chemin: Path) -> dict[str, list[dict]]:
    """Retourne techniques, groupes, logiciels et campagnes ATT&CK."""
    charge = charger_bundle_attack(chemin)
    objets = charge["objets"]

    # index stix_id -> identifiant ATT&CK, pour resoudre les relations 'uses'
    index_attack: dict[str, str] = {}
    for objet in objets:
        identifiant = _identifiant_attack(objet)
        if identifiant:
            index_attack[objet["id"]] = identifiant

    usages: dict[str, list[str]] = {}
    for objet in objets:
        if objet.get("type") != "relationship":
            continue
        if objet.get("relationship_type") != "uses":
            continue
        cible = index_attack.get(objet.get("target_ref", ""))
        source = index_attack.get(objet.get("source_ref", ""))
        if cible and source:
            usages.setdefault(source, []).append(cible)

    techniques: list[dict] = []
    groupes: list[dict] = []
    logiciels: list[dict] = []
    campagnes: list[dict] = []

    for objet in objets:
        genre = objet.get("type")
        identifiant = _identifiant_attack(objet)
        if not identifiant:
            continue
        revoque = bool(objet.get("revoked", False))
        obsolete = bool(objet.get("x_mitre_deprecated", False))

        if genre == "attack-pattern":
            parent = identifiant.split(".")[0] if "." in identifiant else None
            techniques.append(
                {
                    "mitre_id": identifiant,
                    "nom": objet.get("name", ""),
                    "tactiques": _tactiques(objet),
                    "description": nettoyer_attack(objet.get("description")),
                    "sous_technique": bool(objet.get("x_mitre_is_subtechnique", False)),
                    "parent": parent,
                    "plateformes": objet.get("x_mitre_platforms", []) or [],
                    "url": _url_attack(objet),
                    "revoque": revoque,
                    "obsolete": obsolete,
                    "version_attack": objet.get("x_mitre_version"),
                    "stix_id": objet.get("id"),
                }
            )
        elif genre == "intrusion-set":
            groupes.append(
                {
                    "mitre_id": identifiant,
                    "nom": objet.get("name", ""),
                    "alias": objet.get("aliases", []) or [],
                    "description": nettoyer_attack(objet.get("description")),
                    "techniques_utilisees": sorted(set(usages.get(identifiant, []))),
                    "url": _url_attack(objet),
                    "revoque": revoque,
                    "obsolete": obsolete,
                    "stix_id": objet.get("id"),
                }
            )
        elif genre in {"malware", "tool"}:
            logiciels.append(
                {
                    "mitre_id": identifiant,
                    "nom": objet.get("name", ""),
                    "type": genre,
                    "plateformes": objet.get("x_mitre_platforms", []) or [],
                    "description": nettoyer_attack(objet.get("description")),
                    "techniques_utilisees": sorted(set(usages.get(identifiant, []))),
                    "url": _url_attack(objet),
                    "revoque": revoque,
                    "obsolete": obsolete,
                    "stix_id": objet.get("id"),
                }
            )
        elif genre == "campaign":
            campagnes.append(
                {
                    "mitre_id": identifiant,
                    "nom": objet.get("name", ""),
                    "description": nettoyer_attack(objet.get("description")),
                    "premiere_observation": objet.get("first_seen"),
                    "derniere_observation": objet.get("last_seen"),
                    "techniques_utilisees": sorted(set(usages.get(identifiant, []))),
                    "url": _url_attack(objet),
                    "revoque": revoque,
                    "obsolete": obsolete,
                    "stix_id": objet.get("id"),
                }
            )

    techniques.sort(key=lambda t: t["mitre_id"])
    groupes.sort(key=lambda g: g["mitre_id"])
    logiciels.sort(key=lambda s: s["mitre_id"])
    campagnes.sort(key=lambda c: c["mitre_id"])
    return {
        "techniques": techniques,
        "groupes": groupes,
        "logiciels": logiciels,
        "campagnes": campagnes,
    }


def normaliser_kev(chemin: Path) -> tuple[list[dict], dict]:
    with chemin.open(encoding="utf-8") as flux:
        catalogue = json.load(flux)

    enregistrements: list[dict] = []
    for entree in catalogue.get("vulnerabilities", []):
        enregistrements.append(
            {
                "cve_id": entree.get("cveID"),
                "vendeur": entree.get("vendorProject"),
                "produit": entree.get("product"),
                "nom": entree.get("vulnerabilityName"),
                "description": nettoyer(entree.get("shortDescription")),
                "date_ajout": entree.get("dateAdded"),
                "action_attendue": nettoyer(entree.get("requiredAction")),
                "echeance": entree.get("dueDate"),
                "ransomware_connu": entree.get("knownRansomwareCampaignUse"),
                "cwe": entree.get("cwes", []) or [],
                "notes": nettoyer(entree.get("notes")),
            }
        )
    enregistrements.sort(key=lambda e: e["cve_id"])
    entete = {
        "catalogue_version": catalogue.get("catalogVersion"),
        "date_publication": catalogue.get("dateReleased"),
        "nombre_annonce": catalogue.get("count"),
    }
    return enregistrements, entete


def _texte_element(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return nettoyer("".join(element.itertext()))


def normaliser_cwe(chemin_zip: Path) -> tuple[list[dict], dict]:
    with zipfile.ZipFile(chemin_zip) as archive:
        nom_xml = next(n for n in archive.namelist() if n.lower().endswith(".xml"))
        contenu = archive.read(nom_xml)
    racine = ET.parse(io.BytesIO(contenu)).getroot()

    enregistrements: list[dict] = []
    for faiblesse in racine.findall("c:Weaknesses/c:Weakness", NS_CWE):
        numero = faiblesse.get("ID", "")
        methodologies = [
            m.get("Name", "")
            for m in faiblesse.findall(
                "c:Modes_Of_Introduction/c:Introduction/c:Phase", NS_CWE
            )
        ]
        mitigations = [
            _texte_element(m)
            for m in faiblesse.findall(
                "c:Potential_Mitigations/c:Mitigation", NS_CWE
            )
        ]
        consequences = [
            {
                "portee": c.get("Scope", ""),
                "impact": c.get("Impact", ""),
                "note": _texte_element(c.find("c:Note", NS_CWE)),
            }
            for c in faiblesse.findall(
                "c:Common_Consequences/c:Consequence", NS_CWE
            )
        ]
        plateformes = [
            p.get("Name", "")
            for p in faiblesse.findall(
                "c:Applicable_Platforms/c:Language", NS_CWE
            )
        ] + [
            p.get("Name", "")
            for p in faiblesse.findall(
                "c:Applicable_Platforms/c:Technology", NS_CWE
            )
        ]
        enregistrements.append(
            {
                "cwe_id": f"CWE-{numero}",
                "numero": int(numero) if numero.isdigit() else None,
                "nom": faiblesse.get("Name", ""),
                "abstraction": faiblesse.get("Abstraction"),
                "statut": faiblesse.get("Status"),
                "description": _texte_element(faiblesse.find("c:Description", NS_CWE)),
                "description_etendue": _texte_element(
                    faiblesse.find("c:Extended_Description", NS_CWE)
                ),
                "phases_introduction": [m for m in methodologies if m],
                "mitigations": [m for m in mitigations if m],
                "consequences": [c for c in consequences if c["impact"]],
                "plateformes": [p for p in plateformes if p],
                "probabilite_exploitation": faiblesse.get("Likelihood_Of_Exploit"),
                "url": f"https://cwe.mitre.org/data/definitions/{numero}.html",
            }
        )
    enregistrements.sort(key=lambda e: e["numero"] or 0)
    entete = {
        "version_catalogue": racine.get("Version"),
        "date_catalogue": racine.get("Date"),
        "fichier_source": nom_xml,
    }
    return enregistrements, entete


def ecrire_jsonl(enregistrements: list[dict], chemin: Path) -> int:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("w", encoding="utf-8", newline="\n") as flux:
        for enregistrement in enregistrements:
            flux.write(json.dumps(enregistrement, ensure_ascii=False) + "\n")
    return len(enregistrements)
