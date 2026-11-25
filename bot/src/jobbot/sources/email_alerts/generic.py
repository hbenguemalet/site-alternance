"""Parsers « génériques » des alertes e-mail des sites sans parser dédié.

Principe : on cherche dans le mail les liens qui ressemblent à une page d'offre du site (motif
d'URL propre à chaque site), on prend le texte du lien comme titre, et les lignes voisines de la
carte comme entreprise et lieu. Un lien de suivi qui enveloppe l'URL de l'offre (`?url=https%3A…`)
est déballé ; un lien opaque (jeton seul) est ignoré : on ne publie jamais un lien de suivi.
Si un site change de format, il remonte dans la santé du bot (« 0 offre ») et se règle ici.
"""

import re
from collections.abc import Callable
from urllib.parse import unquote

from bs4 import BeautifulSoup

from jobbot.models import Offer
from jobbot.sources.email_alerts.common import card_lines, stable_id

BRUIT = re.compile(
    r"^(voir|postuler|candidater|consulter|d[ée]couvrir|en savoir|afficher|nouveau|new|sponsoris|"
    r"il y a|publi[ée]|aujourd|hier|\d+\s*(?:€|k€|offres?)|cdi|cdd|alternance|stage|apprentissage|"
    r"temps (?:plein|partiel)|[0-9]+%)", re.I)


def make_parser(source: str, offer_rx: str, id_group: int = 1,
                canon: Callable[[str], str] | None = None) -> Callable[[str], list[Offer]]:
    rx = re.compile(offer_rx, re.I)

    def parse(html: str) -> list[Offer]:
        soup = BeautifulSoup(html, "lxml")
        found: dict[str, tuple[str, str, object]] = {}
        for a in soup.find_all("a", href=True):
            href = unquote(a["href"])
            m = rx.search(href)
            if not m:
                continue
            oid = m.group(id_group)
            titre = " ".join(a.stripped_strings)
            if len(titre) < 6 or BRUIT.match(titre):
                continue
            url = canon(m.group(0)) if canon else m.group(0)
            if oid not in found or len(titre) > len(found[oid][0]):
                found[oid] = (titre[:160], url, a)
        offers = []
        for oid, (titre, url, a) in found.items():
            lignes = [x for x in card_lines(a, min_lines=3) if x != titre and not BRUIT.match(x)]
            lignes = [x for x in lignes if len(x) <= 70]
            offers.append(Offer(
                source=source, source_id=oid if len(oid) <= 60 else stable_id(oid), title=titre,
                company=lignes[0] if lignes else None,
                location=lignes[1] if len(lignes) > 1 else "", url=url,
            ))
        return offers

    return parse


# source → (domaine d'expédition, motif de l'URL de l'offre ; le groupe 1 est l'identifiant)
SITES: dict[str, tuple[str, str]] = {
    "wttj": ("welcometothejungle.com", r"https://www\.welcometothejungle\.com/fr/companies/[\w-]+/jobs/([\w-]+)"),
    "jooble": ("jooble.org", r"https://fr\.jooble\.org/(?:desc|emploi)/(-?\d+)"),
    "adzuna": ("adzuna.fr", r"https://www\.adzuna\.fr/(?:details|land/ad)/(\d+)"),
    "freework": ("free-work.com", r"https://www\.free-work\.com/fr/[\w/-]*?/job-mission/([\w-]+)"),
    "jobijoba": ("jobijoba.com", r"https://www\.jobijoba\.com/fr/[\w/-]*?/([\w-]{12,})"),
    "meteojob": ("meteojob.com", r"https://www\.meteojob\.com/(?:jobs|offre)[\w/-]*?/([\w-]{8,})"),
    "wizbii": ("wizbii.com", r"https://www\.wizbii\.com/offre-emploi/([\w-]+)"),
    "jobteaser": ("jobteaser.com", r"https://www\.jobteaser\.com/fr/job-offers/([\w-]+)"),
    "walt": ("walt.community", r"https://(?:www\.)?walt\.community/(?:job|offre)s?/([\w-]+)"),
    "apec": ("apec.fr", r"https://www\.apec\.fr/candidat/recherche-emploi\.html/emploi/detail-offre/([\w]+)"),
    "francetravail": ("francetravail.fr", r"https://candidat\.francetravail\.fr/offres/recherche/detail/(\w+)"),
    "unejeune": ("1jeune1solution.gouv.fr", r"https://www\.1jeune1solution\.gouv\.fr/(?:apprentissage|emplois)/([\w-]+)"),
    "studyrama": ("studyrama-emploi.com", r"https://www\.studyrama-emploi\.com/[\w/-]*?offre[\w/-]*?-(\d+)"),
    "letudiant": ("letudiant.fr", r"https://www\.letudiant\.fr/jobs-stages-alternance/[\w/-]*?-(\d+)\.html"),
    "regionsjob": ("regionsjob.com", r"https://www\.regionsjob\.com/[\w/-]*?offre[\w/-]*?-(\d+)"),
    "labonnealternance": ("apprentissage.beta.gouv.fr", r"https://labonnealternance\.apprentissage\.beta\.gouv\.fr/[\w/?=&.-]*?jobId=([\w-]+)"),
    "glassdoor": ("glassdoor.fr", r"https://www\.glassdoor\.fr/job-listing/[\w/.-]*?jobListingId=(\d+)"),
}
PARSERS = {src: (dom, make_parser(src, rx)) for src, (dom, rx) in SITES.items()}
