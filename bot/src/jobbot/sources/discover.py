"""Découverte automatique de la page carrières et de l'outil de recrutement d'une entreprise.

Pour une entreprise dont on connaît seulement le site, le bot lit sa page d'accueil et ses pages
« carrières » habituelles, et retient :
- la **page des offres d'emploi** (lien « Carrières », « Nous rejoindre »… trouvé sur le site),
  affichée sur la page web à côté de chaque entreprise ;
- l'**outil de recrutement** s'il est géré par `careers.py` (Greenhouse, Lever, Ashby, Workable,
  Recruitee, SmartRecruiters) : l'entreprise rejoint alors la source « carrières » et le bot lit
  TOUTES ses offres en ligne, y compris celles publiées avant tes alertes e-mail.

Le résultat est mémorisé (data/ats_decouverts.json). Une entreprise sans outil connu est
réessayée une fois par semaine.
"""

import json
import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

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
PAGES_ATS = {"greenhouse": "https://boards.greenhouse.io/{}", "lever": "https://jobs.lever.co/{}",
             "ashby": "https://jobs.ashbyhq.com/{}", "workable": "https://apply.workable.com/{}/",
             "recruitee": "https://{}.recruitee.com", "smartrecruiters": "https://jobs.smartrecruiters.com/{}"}
FORT = re.compile(r"carri[èe]res?|recrutement|nous rejoindre|rejoignez|offres? d.emploi|travailler (?:chez|avec)|careers?|join us|work with us", re.I)
FAIBLE = re.compile(r"\bemplois?\b|\bjobs?\b|\brecrut", re.I)
SOCIAL = re.compile(r"linkedin|facebook|twitter|x\.com|instagram|youtube|tiktok|welcometothejungle|indeed|glassdoor", re.I)
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


def lien_carrieres(html: str, base: str) -> str | None:
    """Lien « carrières / offres d'emploi » d'une page d'accueil (texte du lien d'abord, puis adresse)."""
    faible = None
    for a in BeautifulSoup(html or "", "lxml").find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        url = urljoin(base, href)
        hote = url.split("/")[2] if url.count("/") >= 2 else url
        if SOCIAL.search(hote):
            continue
        texte = " ".join(a.stripped_strings)[:80]
        if FORT.search(texte) or FORT.search(url):
            return url
        if faible is None and FAIBLE.search(texte) and len(texte) < 40:
            faible = url
    return faible


def chercher(client: httpx.Client, url: str, limite: float | None = None) -> dict:
    """{"ats", "id", "page"} : outil de recrutement et page des offres (None si introuvables)."""
    base = url.rstrip("/")
    page = None
    for chemin in CHEMINS:
        if limite is not None and time.time() > limite:
            break
        try:
            r = client.get(base + chemin)
        except httpx.HTTPError:
            if chemin == "":  # le site ne répond pas du tout : inutile d'essayer les autres pages
                break
            continue
        if r.status_code != 200:
            continue
        if chemin == "":
            page = lien_carrieres(r.text, str(r.url))
        elif page is None:
            page = str(r.url)  # une page « /carrieres » qui répond fait l'affaire
        if found := detecter(r.text):
            return {"ats": found[0], "id": found[1], "page": page or PAGES_ATS[found[0]].format(found[1])}
    return {"ats": None, "id": None, "page": page}


def decouvrir(entreprises: list[dict], cache: Path, deja: list[dict], client: httpx.Client | None = None) -> list[dict]:
    """Entreprises {nom, ats, id} trouvées à partir de [{nom, url}], sans doublon avec `deja`.
    Plusieurs sites sont interrogés en parallèle, dans la limite de BUDGET_S secondes."""
    memoire = json.loads(cache.read_text()) if cache.exists() else {}
    client = client or httpx.Client(timeout=6, follow_redirects=True,
                                    headers={"User-Agent": "jobbot (offres d'emploi perso)"})
    maintenant = time.time()
    limite = maintenant + BUDGET_S

    def a_refaire(m: dict | None) -> bool:
        if m is None or "page" not in m:  # jamais cherché (ou ancien format sans page des offres)
            return True
        return not m.get("ats") and maintenant - m.get("essai", 0) > SEMAINE

    a_chercher = [e for e in entreprises if a_refaire(memoire.get(e["nom"]))]
    with ThreadPoolExecutor(max_workers=8) as pool:
        trouves = list(pool.map(lambda e: chercher(client, e["url"], limite), a_chercher))
    for e, f in zip(a_chercher, trouves):
        if time.time() > limite and not f["page"] and not f["ats"]:
            continue  # pas eu le temps : on réessaiera au prochain passage
        memoire[e["nom"]] = {**f, "essai": maintenant}
        log.info("découverte : %s → %s", e["nom"], f"{f['ats']}/{f['id']}" if f["ats"] else f"pas d'outil connu, page : {f['page']}")
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


def pages(cache: Path) -> dict[str, str]:
    """nom → page des offres d'emploi, pour la page web."""
    if not cache.exists():
        return {}
    return {nom: m["page"] for nom, m in json.loads(cache.read_text()).items() if m.get("page")}
