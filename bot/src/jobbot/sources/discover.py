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
from concurrent.futures import ThreadPoolExecutor
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
BUDGET_S = 150  # au-delà, on s'arrête : les entreprises restantes seront cherchées au passage suivant


def detecter(html: str) -> tuple[str, str] | None:
    """(outil, identifiant) du premier outil de recrutement cité dans la page, sinon None."""
    for ats, rx in MOTIFS:
        for m in rx.finditer(html or ""):
            ident = m.group(1)
            if ident.lower() not in INVALIDES:
                return ats, ident
    return None


def chercher(client: httpx.Client, url: str, limite: float | None = None) -> tuple[str, str] | None:
    base = url.rstrip("/")
    for chemin in CHEMINS:
        if limite is not None and time.time() > limite:
            return None
        try:
            r = client.get(base + chemin)
        except httpx.HTTPError:
            if chemin == "":  # le site ne répond pas du tout : inutile d'essayer les autres pages
                return None
            continue
        if r.status_code == 200 and (found := detecter(r.text)):
            return found
    return None


def decouvrir(entreprises: list[dict], cache: Path, deja: list[dict], client: httpx.Client | None = None) -> list[dict]:
    """Entreprises {nom, ats, id} trouvées à partir de [{nom, url}], sans doublon avec `deja`.
    Plusieurs sites sont interrogés en parallèle, dans la limite de BUDGET_S secondes."""
    memoire = json.loads(cache.read_text()) if cache.exists() else {}
    client = client or httpx.Client(timeout=6, follow_redirects=True,
                                    headers={"User-Agent": "jobbot (offres d'emploi perso)"})
    maintenant = time.time()
    limite = maintenant + BUDGET_S
    a_chercher = [e for e in entreprises
                  if (m := memoire.get(e["nom"])) is None or (not m.get("ats") and maintenant - m.get("essai", 0) > SEMAINE)]
    with ThreadPoolExecutor(max_workers=8) as pool:
        trouves = list(pool.map(lambda e: chercher(client, e["url"], limite), a_chercher))
    for e, f in zip(a_chercher, trouves):
        if f is None and time.time() > limite:
            continue  # pas eu le temps : on réessaiera au prochain passage
        memoire[e["nom"]] = {"ats": f[0], "id": f[1]} if f else {"ats": None, "essai": maintenant}
        log.info("découverte : %s → %s", e["nom"], f"{f[0]}/{f[1]}" if f else "aucun outil connu")
    connus = {(e["ats"], e["id"].lower()) for e in deja}
    out = []
    for e in entreprises:
        m = memoire.get(e["nom"]) or {}
        if m.get("ats") and (m["ats"], m["id"].lower()) not in connus:
            connus.add((m["ats"], m["id"].lower()))
            out.append({"nom": e["nom"], "ats": m["ats"], "id": m["id"]})
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(memoire, ensure_ascii=False, indent=1))
    return out
