"""Source : API « Offres d'emploi v2 » de France Travail (officielle, gratuite).

Clés : compte sur https://francetravail.io → créer une application, activer l'API « Offres d'emploi »
→ FT_CLIENT_ID et FT_CLIENT_SECRET (secrets GitHub). Jeton OAuth2 « client credentials ».
On cherche des contrats d'apprentissage (natureContrat E2) et de professionnalisation (E1)
autour des villes de config.yaml, avec les mots-clés de `francetravail.mots_cles`.
"""

import logging

import httpx

from jobbot.models import Offer

log = logging.getLogger(__name__)

TOKEN = "https://entreprise.francetravail.fr/connexion/oauth2/access_token"
SEARCH = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
DETAIL = "https://candidat.francetravail.fr/offres/recherche/detail/"


class FTError(RuntimeError):
    pass


def to_offer(j: dict, city_key: str) -> Offer | None:
    if not j.get("id") or not j.get("intitule"):
        return None
    lieu = (j.get("lieuTravail") or {}).get("libelle") or ""
    return Offer(
        source="francetravail", source_id=str(j["id"]), title=j["intitule"].strip(),
        company=((j.get("entreprise") or {}).get("nom") or "").strip() or None, location=lieu,
        url=(j.get("origineOffre") or {}).get("urlOrigine") or DETAIL + str(j["id"]),
        description=j.get("description") or "", contract="alternance", city_key=city_key,
    )


class FranceTravail:
    name = "francetravail"

    def __init__(self, client_id: str, secret: str, villes: dict, mots_cles: list[str],
                 rayon_km: int = 30, client: httpx.Client | None = None):
        self.cid, self.secret, self.mots = client_id, secret, mots_cles
        self.rayon = rayon_km
        # code INSEE de la commune centre (champ `insee` de la ville dans config.yaml)
        self.points = {k: v["insee"] for k, v in villes.items() if v.get("insee")}
        self.client = client or httpx.Client(timeout=25)

    def token(self) -> str:
        r = self.client.post(TOKEN, params={"realm": "/partenaire"}, data={
            "grant_type": "client_credentials", "client_id": self.cid, "client_secret": self.secret,
            "scope": "api_offresdemploiv2 o2dsoffre"})
        if r.status_code >= 400:
            raise FTError(f"jeton France Travail refusé (HTTP {r.status_code}) : vérifier FT_CLIENT_ID / FT_CLIENT_SECRET")
        return r.json()["access_token"]

    def fetch(self) -> list[Offer]:
        headers = {"Authorization": f"Bearer {self.token()}", "Accept": "application/json"}
        offers, seen = [], set()
        for city, insee in self.points.items():
            for mot in self.mots:
                r = self.client.get(SEARCH, headers=headers, params={
                    "motsCles": mot, "commune": insee, "distance": self.rayon,
                    "natureContrat": "E1,E2", "range": "0-149", "sort": 1})
                if r.status_code == 204:  # aucune offre
                    continue
                if r.status_code >= 400:
                    raise FTError(f"API France Travail : HTTP {r.status_code}")
                for j in r.json().get("resultats", []):
                    o = to_offer(j, city)
                    if o and o.source_id not in seen:
                        seen.add(o.source_id)
                        offers.append(o)
            log.info("France Travail [%s] : %d offres", city, len(offers))
        return offers
