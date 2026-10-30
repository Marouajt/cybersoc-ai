"""Reconstruction complete des donnees (`make data`) — etape 1, bloc B.

Pipeline :
    raw (STIX / KEV / CWE)  ->  processed/*.jsonl  ->  chunks.jsonl  ->  ids/*.txt

Chaque etape est deterministe : meme entree (verifiee par SHA-256) et meme code
produisent les memes fichiers. C'est la condition pour que l'etape 12 puisse
comparer des modeles sans se demander si les donnees ont bouge.

Usage :
    python -m data.build_all              # telecharge si besoin puis reconstruit
    python -m data.build_all --offline    # utilise data/raw/ tel quel
    python -m data.build_all --force      # force le re-telechargement
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from data import chunking, ingest
from data.sources import (
    DOSSIER_PROCESSED,
    SOURCES,
    decrire,
    ecrire_manifeste,
    telecharger,
)

AVERTISSEMENT_CVE = (
    "cve_ids.txt ne contient que les CVE du catalogue CISA KEV (exploitees "
    "dans la nature). Une CVE reelle absente de KEV n'y figure pas : la "
    "metrique d'hallucination de l'etape 2 doit donc etre lue comme "
    "'identifiant valide dans le perimetre de connaissance du systeme'."
)

AVERTISSEMENT_MITRE = (
    "mitre_ids.txt contient tous les identifiants ATT&CK existants, y compris "
    "les objets obsoletes ou revoques : un identifiant existant n'est pas un "
    "identifiant a jour. Les chunks, eux, excluent les objets obsoletes."
)


def cle_naturelle(valeur: str) -> list[object]:
    """Tri naturel : T1059.9 avant T1059.10, CVE-2021-2 avant CVE-2021-10."""
    morceaux: list[object] = []
    for bloc in valeur.replace("-", ".").split("."):
        morceaux.append(int(bloc) if bloc.isdigit() else bloc)
    return morceaux


def _ecrire_liste(identifiants: list[str], chemin: Path) -> dict:
    uniques = sorted(set(identifiants), key=cle_naturelle)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    contenu = "\n".join(uniques) + "\n"
    chemin.write_text(contenu, encoding="utf-8", newline="\n")
    return {
        "fichier": str(chemin.relative_to(DOSSIER_PROCESSED.parent.parent)).replace(
            "\\", "/"
        ),
        "entrees": len(uniques),
        "sha256": hashlib.sha256(contenu.encode("utf-8")).hexdigest(),
    }


def construire(offline: bool = False, force: bool = False) -> dict:
    DOSSIER_PROCESSED.mkdir(parents=True, exist_ok=True)

    # --- 1. acquisition -----------------------------------------------------
    for source in SOURCES:
        if offline:
            chemin = DOSSIER_PROCESSED.parent / "raw" / source.fichier
            if not chemin.exists():
                raise SystemExit(
                    f"Mode hors ligne : {chemin} absent. "
                    "Lancez sans --offline pour telecharger les sources."
                )
        else:
            telecharger(source, force=force)

    # --- 2. normalisation ---------------------------------------------------
    attack = ingest.normaliser_mitre(DOSSIER_PROCESSED.parent / "raw"
                                     / "enterprise-attack.json")
    cves, entete_kev = ingest.normaliser_kev(
        DOSSIER_PROCESSED.parent / "raw" / "known_exploited_vulnerabilities.json"
    )
    faiblesses, entete_cwe = ingest.normaliser_cwe(
        DOSSIER_PROCESSED.parent / "raw" / "cwec_latest.xml.zip"
    )

    compteurs = {
        "mitre_techniques": ingest.ecrire_jsonl(
            attack["techniques"], DOSSIER_PROCESSED / "mitre_techniques.jsonl"
        ),
        "mitre_groupes": ingest.ecrire_jsonl(
            attack["groupes"], DOSSIER_PROCESSED / "mitre_groupes.jsonl"
        ),
        "mitre_logiciels": ingest.ecrire_jsonl(
            attack["logiciels"], DOSSIER_PROCESSED / "mitre_logiciels.jsonl"
        ),
        "mitre_campagnes": ingest.ecrire_jsonl(
            attack["campagnes"], DOSSIER_PROCESSED / "mitre_campagnes.jsonl"
        ),
        "kev_cves": ingest.ecrire_jsonl(cves, DOSSIER_PROCESSED / "kev_cves.jsonl"),
        "cwe_faiblesses": ingest.ecrire_jsonl(
            faiblesses, DOSSIER_PROCESSED / "cwe_faiblesses.jsonl"
        ),
    }

    # --- 3. chunking --------------------------------------------------------
    donnees = {
        "techniques": attack["techniques"],
        "groupes": attack["groupes"],
        "logiciels": attack["logiciels"],
        "campagnes": attack["campagnes"],
        "cves": cves,
        "cwe": faiblesses,
    }
    chunks = chunking.construire_chunks(donnees)
    fichier_chunks = DOSSIER_PROCESSED / "chunks.jsonl"
    ingest.ecrire_jsonl(chunks, fichier_chunks)
    stats_chunks = chunking.statistiques(chunks)
    stats_chunks["fichier"] = "data/processed/chunks.jsonl"
    stats_chunks["versionne"] = False
    stats_chunks["sha256"] = hashlib.sha256(fichier_chunks.read_bytes()).hexdigest()
    stats_chunks["regenerer_avec"] = "python -m data.build_all --offline"

    # --- 4. listes d'identifiants valides -----------------------------------
    ids_mitre = [
        objet["mitre_id"]
        for cle in ("techniques", "groupes", "logiciels", "campagnes")
        for objet in attack[cle]
    ]
    ids_cve = [cve["cve_id"] for cve in cves]
    ids_cwe = [faiblesse["cwe_id"] for faiblesse in faiblesses]

    listes = {
        "mitre": _ecrire_liste(ids_mitre, DOSSIER_PROCESSED / "mitre_ids.txt"),
        "cve": _ecrire_liste(ids_cve, DOSSIER_PROCESSED / "cve_ids.txt"),
        "cwe": _ecrire_liste(ids_cwe, DOSSIER_PROCESSED / "cwe_ids.txt"),
    }
    listes["mitre"]["avertissement"] = AVERTISSEMENT_MITRE
    listes["cve"]["avertissement"] = AVERTISSEMENT_CVE
    listes["cwe"]["avertissement"] = (
        "cwe_ids.txt couvre le catalogue CWE complet (toutes abstractions, "
        "y compris les faiblesses obsoletes)."
    )

    # --- 5. manifeste -------------------------------------------------------
    fiches = [
        decrire(SOURCES[0], len(attack["techniques"])),
        decrire(SOURCES[1], len(cves)),
        decrire(SOURCES[2], len(faiblesses)),
    ]
    fichier_manifeste = ecrire_manifeste(fiches)
    manifeste = json.loads(fichier_manifeste.read_text(encoding="utf-8"))
    manifeste["enregistrements"] = compteurs
    manifeste["entetes_sources"] = {"kev": entete_kev, "cwe": entete_cwe}
    manifeste["chunks"] = stats_chunks
    manifeste["listes_identifiants"] = listes
    fichier_manifeste.write_text(
        json.dumps(manifeste, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    return {"compteurs": compteurs, "chunks": stats_chunks, "listes": listes}


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--offline", action="store_true", help="pas de reseau")
    analyseur.add_argument("--force", action="store_true", help="re-telecharger")
    arguments = analyseur.parse_args(argv)

    resultat = construire(offline=arguments.offline, force=arguments.force)

    print("Donnees reconstruites :")
    for nom, nombre in resultat["compteurs"].items():
        print(f"  {nom:<18} {nombre:>6}")
    stats = resultat["chunks"]
    print(
        f"  chunks             {stats['total_chunks']:>6}  "
        f"({stats['tokens_min']}-{stats['tokens_max']} tokens, "
        f"moyenne {stats['tokens_moyen']})"
    )
    print(f"  repartition        {stats['par_type']}")
    print("Identifiants valides :")
    for nom, fiche in resultat["listes"].items():
        print(f"  {nom + '_ids.txt':<14} {fiche['entrees']:>6}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
