"""Découverte automatique de l'outil de recrutement d'une entreprise.

Pour une entreprise dont on connaît seulement le site, on lit sa page d'accueil et ses pages
« carrières » habituelles, et on cherche un lien vers un outil géré par `careers.py` (Greenhouse,
Lever, Ashby, Workable, Recruitee, SmartRecruiters). Trouvé, l'entreprise rejoint la source
« carrières » : le bot lit alors TOUTES ses offres en ligne, y compris celles publiées avant
la création de tes alertes e-mail (les alertes, elles, n'envoient que les nouveautés).

Le résultat est mémorisé (data/ats_decouverts.json) : une entreprise trouvée n'est plus cherchée,
une entreprise sans outil connu est réessayée une fois par semaine.
"""

import json
import logging
import re
import time
from pathlib import Path

import httpx

log = logging.getLogger(__name__)

CHEMINS = ["", "/carrieres", "/careers", "/jobs", "/recrutement", "/fr/carrieres", "/emploi", "/nous-rejoindre"]
INVALIDES = {"embed", "api", "v1", "v0", "www", "widget", "static", "assets", "jobs", "careers", "company", "companies"}
MOTIFS = [
    ("greenhouse", re.compile(r"(?:boards|job-boards)(?:-api)?\.greenhouse\.io/(?:embed/job_board\?for=|v1/boards/)?([\w-]+)", re.I)),
    ("lever", re.compile(r"jobs\.(?:eu\.)?lever\.co/([\w-]+)", re.I)),
    ("ashby", re.compile(r"jobs\.ashbyhq\.com/([\w.%-]+)", re.I)),
    ("workable", re.compile(r"apply\.workable\.com/([\w-]+)", re.I)),
    ("recruitee", re.compile(r"([\w-]+)\.recruitee\.com", re.I)),
    ("smartrecruiters", re.compile(r"(?:jobs|careers)\.smartrecruiters\.com/([\w-]+)", re.I)),
]
SEMAINE = 7 * 86400


def detecter(html: str) -> tuple[str, str] | None:
    """(outil, identifiant) du premier outil de recrutement cité dans la page, sinon None."""
    for ats, rx in MOTIFS:
        for m in rx.finditer(html or ""):
            ident = m.group(1)
            if ident.lower() not in INVALIDES:
                return ats, ident
    return None


def chercher(client: httpx.Client, url: str) -> tuple[str, str] | None:
    base = url.rstrip("/")
    pages = [base] if "/" in base.split("//", 1)[-1] else [base + c for c in CHEMINS]
    pages += [base + c for c in CHEMINS if base + c not in pages] if len(pages) == 1 else []
    for page in pages:
        try:
            r = client.get(page)
        except httpx.HTTPError:
            continue
        if r.status_code == 200 and (found := detecter(r.text)):
            return found
    return None


def decouvrir(entreprises: list[dict], cache: Path, deja: list[dict], client: httpx.Client | None = None) -> list[dict]:
    """Entreprises {nom, ats, id} trouvées à partir de [{nom, url}], sans doublon avec `deja`."""
    memoire = json.loads(cache.read_text()) if cache.exists() else {}
    client = client or httpx.Client(timeout=8, follow_redirects=True,
                                    headers={"User-Agent": "jobbot (offres d'emploi perso)"})
    connus = {(e["ats"], e["id"].lower()) for e in deja}
    out, maintenant = [], time.time()
    for e in entreprises:
        m = memoire.get(e["nom"])
        if m is None or (not m.get("ats") and maintenant - m.get("essai", 0) > SEMAINE):
            f = chercher(client, e["url"])
            m = memoire[e["nom"]] = {"ats": f[0], "id": f[1]} if f else {"ats": None, "essai": maintenant}
            log.info("découverte : %s → %s", e["nom"], f"{f[0]}/{f[1]}" if f else "aucun outil connu")
        if m.get("ats") and (m["ats"], m["id"].lower()) not in connus:
            connus.add((m["ats"], m["id"].lower()))
            out.append({"nom": e["nom"], "ats": m["ats"], "id": m["id"]})
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(memoire, ensure_ascii=False, indent=1))
    return out
