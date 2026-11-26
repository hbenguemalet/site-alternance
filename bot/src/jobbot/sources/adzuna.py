"""Source : API Adzuna (agrégateur d'offres, gratuite, clé immédiate).

Compte sur https://developer.adzuna.com → « Register » → ADZUNA_APP_ID et ADZUNA_APP_KEY.
Contrairement aux alertes e-mail, l'API renvoie TOUTES les offres en ligne qui correspondent
à la recherche, y compris celles publiées avant la création de tes alertes.
Route : GET /v1/api/jobs/fr/search/<page>?what=…&where=…&distance=…
"""

import logging

import httpx

from jobbot.models import Offer

log = logging.getLogger(__name__)

ENDPOINT = "https://api.adzuna.com/v1/api/jobs/fr/search/{page}"


class AdzunaError(RuntimeError):
    pass


def to_offer(j: dict, city_key: str) -> Offer | None:
    if not j.get("id") or not j.get("title"):
        return None
    return Offer(
        source="adzuna", source_id=str(j["id"]), title=" ".join(j["title"].replace("<strong>", "").replace("</strong>", "").split()),
        company=((j.get("company") or {}).get("display_name") or "").strip() or None,
        location=(j.get("location") or {}).get("display_name") or "", url=j.get("redirect_url") or "",
        description=j.get("description") or "", contract=j.get("contract_type") or j.get("contract_time"),
        city_key=city_key,
    )


class Adzuna:
    name = "adzuna"

    def __init__(self, app_id: str, app_key: str, villes: dict, mots_cles: list[str], rayon_km: int = 30,
                 pages: int = 2, client: httpx.Client | None = None):
        self.app_id, self.app_key, self.mots, self.rayon, self.pages = app_id, app_key, mots_cles, rayon_km, pages
        self.villes = {k: v["adzuna_where"] for k, v in villes.items() if v.get("adzuna_where")}
        self.client = client or httpx.Client(timeout=25)

    def fetch(self) -> list[Offer]:
        offers, seen = [], set()
        for city, where in self.villes.items():
            for mot in self.mots:
                for page in range(1, self.pages + 1):
                    r = self.client.get(ENDPOINT.format(page=page), params={
                        "app_id": self.app_id, "app_key": self.app_key, "what": mot, "where": where,
                        "distance": self.rayon, "results_per_page": 50, "sort_by": "date",
                        "content-type": "application/json"})
                    if r.status_code in (401, 403):
                        raise AdzunaError("clé Adzuna refusée : vérifier ADZUNA_APP_ID / ADZUNA_APP_KEY")
                    if r.status_code >= 400:
                        raise AdzunaError(f"API Adzuna : HTTP {r.status_code}")
                    results = r.json().get("results", [])
                    for j in results:
                        o = to_offer(j, city)
                        if o and o.url and o.source_id not in seen:
                            seen.add(o.source_id)
                            offers.append(o)
                    if len(results) < 50:
                        break
            log.info("Adzuna [%s] : %d offres au total", city, len(offers))
        return offers
