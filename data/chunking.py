"""Decoupage en chunks avec metadonnees (bloc B, tache 8).

Deux regles de la feuille de route sont appliquees ici :

  * un chunk par objet de connaissance (technique, CVE, CWE) — la granularite
    d'un objet est celle de la question qu'on posera au modele ;
  * 300 a 500 tokens avec 10 a 15 % de chevauchement pour les textes longs
    (rapports CTI, descriptions CWE etendues).

Le comptage de tokens est une approximation (4 caracteres ~ 1 token). Elle est
declaree dans le manifeste (`tokenizer`) pour que l'etape 3 puisse la remplacer
par le tokenizer reel du modele sans casser les comparaisons : le champ
`tokenizer` voyage avec les chunks.
"""

from __future__ import annotations

import re

TOKENIZER_ID = "approx_chars_div_4"
CIBLE_TOKENS = 400
MAX_TOKENS = 500
CHEVAUCHEMENT = 0.12

COUPURE_PHRASE = re.compile(r"(?<=[.!?])\s+")


def estimer_tokens(texte: str) -> int:
    """Estimation volontairement grossiere et stable (4 caracteres = 1 token)."""
    return max(1, round(len(texte) / 4))


def _decouper_longue_phrase(phrase: str, maximum: int = MAX_TOKENS) -> list[str]:
    """Secours pour une phrase plus longue qu'un chunk entier."""
    limite = maximum * 4
    morceaux = []
    reste = phrase
    while len(reste) > limite:
        coupe = reste.rfind(" ", 0, limite)
        coupe = coupe if coupe > limite // 2 else limite
        morceaux.append(reste[:coupe].strip())
        reste = reste[coupe:].strip()
    if reste:
        morceaux.append(reste)
    return morceaux


def phrases(texte: str) -> list[str]:
    unites: list[str] = []
    for paragraphe in texte.split("\n\n"):
        paragraphe = paragraphe.strip()
        if not paragraphe:
            continue
        for phrase in COUPURE_PHRASE.split(paragraphe):
            phrase = phrase.strip()
            if not phrase:
                continue
            if estimer_tokens(phrase) > MAX_TOKENS:
                unites.extend(_decouper_longue_phrase(phrase))
            else:
                unites.append(phrase)
    return unites


def decouper(
    texte: str,
    cible: int = CIBLE_TOKENS,
    maximum: int = MAX_TOKENS,
    chevauchement: float = CHEVAUCHEMENT,
) -> list[str]:
    """Decoupe un texte en fenetres de ~cible tokens, avec recouvrement."""
    texte = texte.strip()
    if not texte:
        return []
    if estimer_tokens(texte) <= maximum:
        return [texte]

    unites = phrases(texte)
    if not unites:
        return [texte]

    morceaux: list[str] = []
    debut = 0
    while debut < len(unites):
        fin = debut
        courant = ""
        while fin < len(unites):
            candidat = f"{courant} {unites[fin]}".strip() if courant else unites[fin]
            trop_long = estimer_tokens(candidat) > maximum
            if trop_long and courant:
                break
            courant = candidat
            fin += 1
        morceaux.append(courant)

        if fin >= len(unites):
            break

        budget = max(1, int(estimer_tokens(courant) * chevauchement))
        arriere = fin
        repris = 0
        while arriere - 1 > debut and repris < budget:
            arriere -= 1
            repris += estimer_tokens(unites[arriere])
        debut = arriere if arriere > debut else fin

        if fin <= debut:  # securite anti-boucle infinie
            debut = fin

    return [m for m in morceaux if m]


def _texte_technique(enregistrement: dict) -> str:
    lignes = [
        f"{enregistrement['mitre_id']} — {enregistrement['nom']}",
        f"Tactiques : {', '.join(enregistrement['tactiques']) or 'non precisees'}",
    ]
    if enregistrement.get("plateformes"):
        lignes.append(f"Plateformes : {', '.join(enregistrement['plateformes'])}")
    if enregistrement.get("parent"):
        lignes.append(f"Sous-technique de : {enregistrement['parent']}")
    return "\n".join(lignes) + "\n\n" + enregistrement.get("description", "")


def _texte_cve(enregistrement: dict) -> str:
    lignes = [
        f"{enregistrement['cve_id']} — {enregistrement['vendeur']} "
        f"{enregistrement['produit']}",
        enregistrement.get("nom", ""),
        "",
        enregistrement.get("description", ""),
        "",
        f"Action attendue : {enregistrement.get('action_attendue', '')}",
        f"Ransomware connu : {enregistrement.get('ransomware_connu', 'Unknown')}",
    ]
    if enregistrement.get("cwe"):
        lignes.append(f"Faiblesses associees : {', '.join(enregistrement['cwe'])}")
    lignes.append(f"Ajoutee au catalogue KEV le : {enregistrement.get('date_ajout')}")
    return "\n".join(lignes)


def _texte_cwe(enregistrement: dict) -> str:
    lignes = [
        f"{enregistrement['cwe_id']} — {enregistrement['nom']}",
        f"Abstraction : {enregistrement.get('abstraction') or 'non precisee'}",
        "",
        enregistrement.get("description", ""),
    ]
    if enregistrement.get("description_etendue"):
        lignes.extend(["", enregistrement["description_etendue"]])
    if enregistrement.get("mitigations"):
        lignes.extend(["", "Mitigations :"])
        lignes.extend(f"- {m}" for m in enregistrement["mitigations"])
    if enregistrement.get("consequences"):
        couples = {
            (c.get("portee", ""), c.get("impact", ""))
            for c in enregistrement["consequences"]
        }
        lignes.extend(
            ["", "Consequences : " + ", ".join(f"{p} / {i}" for p, i in sorted(couples))]
        )
    return "\n".join(lignes)


def _texte_rapport(enregistrement: dict, genre: str) -> str:
    lignes = [
        f"{enregistrement['mitre_id']} — {enregistrement['nom']}",
        f"Type : {genre}",
    ]
    if enregistrement.get("alias"):
        lignes.append(f"Alias : {', '.join(enregistrement['alias'])}")
    if enregistrement.get("techniques_utilisees"):
        lignes.append(
            "Techniques observees : "
            + ", ".join(enregistrement["techniques_utilisees"])
        )
    return "\n".join(lignes) + "\n\n" + enregistrement.get("description", "")


def _fabriquer(
    doc_id: str,
    doc_type: str,
    source: str,
    titre: str,
    texte: str,
    meta: dict,
    chevauchement: float = CHEVAUCHEMENT,
) -> list[dict]:
    morceaux = decouper(texte, chevauchement=chevauchement)
    chunks = []
    for position, morceau in enumerate(morceaux):
        chunks.append(
            {
                "chunk_id": f"{doc_id}#{position}",
                "doc_id": doc_id,
                "doc_type": doc_type,
                "source": source,
                "titre": titre,
                "position": position,
                "nb_morceaux": len(morceaux),
                "tokens": estimer_tokens(morceau),
                "tokenizer": TOKENIZER_ID,
                "texte": morceau,
                "meta": meta,
            }
        )
    return chunks


def construire_chunks(donnees: dict) -> list[dict]:
    """Transforme les enregistrements normalises en chunks prets pour l'indexation."""
    chunks: list[dict] = []

    for technique in donnees.get("techniques", []):
        if technique.get("revoque") or technique.get("obsolete"):
            continue
        chunks.extend(
            _fabriquer(
                doc_id=f"mitre:{technique['mitre_id']}",
                doc_type="technique",
                source="mitre_attack_enterprise",
                titre=f"{technique['mitre_id']} {technique['nom']}",
                texte=_texte_technique(technique),
                meta={
                    "mitre_id": technique["mitre_id"],
                    "tactiques": technique["tactiques"],
                    "plateformes": technique["plateformes"],
                    "sous_technique": technique["sous_technique"],
                    "url": technique.get("url"),
                },
            )
        )

    for groupe in donnees.get("groupes", []):
        if groupe.get("revoque") or groupe.get("obsolete"):
            continue
        chunks.extend(
            _fabriquer(
                doc_id=f"mitre:{groupe['mitre_id']}",
                doc_type="groupe",
                source="mitre_attack_enterprise",
                titre=f"{groupe['mitre_id']} {groupe['nom']}",
                texte=_texte_rapport(groupe, "groupe APT"),
                meta={
                    "mitre_id": groupe["mitre_id"],
                    "alias": groupe.get("alias", []),
                    "url": groupe.get("url"),
                },
            )
        )

    for campagne in donnees.get("campagnes", []):
        if campagne.get("revoque") or campagne.get("obsolete"):
            continue
        chunks.extend(
            _fabriquer(
                doc_id=f"mitre:{campagne['mitre_id']}",
                doc_type="campagne",
                source="mitre_attack_enterprise",
                titre=f"{campagne['mitre_id']} {campagne['nom']}",
                texte=_texte_rapport(campagne, "campagne"),
                meta={
                    "mitre_id": campagne["mitre_id"],
                    "url": campagne.get("url"),
                },
            )
        )

    for logiciel in donnees.get("logiciels", []):
        if logiciel.get("revoque") or logiciel.get("obsolete"):
            continue
        chunks.extend(
            _fabriquer(
                doc_id=f"mitre:{logiciel['mitre_id']}",
                doc_type="logiciel",
                source="mitre_attack_enterprise",
                titre=f"{logiciel['mitre_id']} {logiciel['nom']}",
                texte=_texte_rapport(logiciel, logiciel["type"]),
                meta={
                    "mitre_id": logiciel["mitre_id"],
                    "type": logiciel["type"],
                    "plateformes": logiciel.get("plateformes", []),
                    "url": logiciel.get("url"),
                },
            )
        )

    for cve in donnees.get("cves", []):
        chunks.extend(
            _fabriquer(
                doc_id=f"cve:{cve['cve_id']}",
                doc_type="cve",
                source="cisa_kev",
                titre=f"{cve['cve_id']} {cve['vendeur']} {cve['produit']}",
                texte=_texte_cve(cve),
                meta={
                    "cve_id": cve["cve_id"],
                    "vendeur": cve["vendeur"],
                    "produit": cve["produit"],
                    "ransomware_connu": cve.get("ransomware_connu"),
                    "cwe": cve.get("cwe", []),
                },
            )
        )

    for faiblesse in donnees.get("cwe", []):
        chunks.extend(
            _fabriquer(
                doc_id=f"cwe:{faiblesse['cwe_id']}",
                doc_type="cwe",
                source="mitre_cwe",
                titre=f"{faiblesse['cwe_id']} {faiblesse['nom']}",
                texte=_texte_cwe(faiblesse),
                meta={
                    "cwe_id": faiblesse["cwe_id"],
                    "abstraction": faiblesse.get("abstraction"),
                    "url": faiblesse.get("url"),
                },
            )
        )

    return chunks


def statistiques(chunks: list[dict]) -> dict:
    par_type: dict[str, int] = {}
    for chunk in chunks:
        par_type[chunk["doc_type"]] = par_type.get(chunk["doc_type"], 0) + 1
    tokens = [c["tokens"] for c in chunks] or [0]
    return {
        "total_chunks": len(chunks),
        "par_type": dict(sorted(par_type.items())),
        "tokens_min": min(tokens),
        "tokens_max": max(tokens),
        "tokens_moyen": round(sum(tokens) / len(tokens)),
        "chunks_superieurs_500": sum(1 for t in tokens if t > MAX_TOKENS),
    }
