import httpx
import pytest

from jobbot.sources.adzuna import Adzuna, AdzunaError, to_offer

VILLES = {"lille": {"adzuna_where": "Lille"}}
JOB = {"id": 42, "title": "Alternance <strong>Data</strong> Analyst", "company": {"display_name": "Acme"},
       "location": {"display_name": "Lille, Nord"}, "redirect_url": "https://www.adzuna.fr/land/ad/42",
       "contract_time": "full_time"}


def client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_to_offer_nettoie_le_titre():
    o = to_offer(JOB, "lille")
    assert o.title == "Alternance Data Analyst" and o.company == "Acme" and o.city_key == "lille"


def test_fetch_dedoublonne_et_s_arrete_a_la_derniere_page():
    appels = []

    def h(req):
        appels.append(req.url.params["what"])
        return httpx.Response(200, json={"results": [JOB]})
    out = Adzuna("i", "k", VILLES, ["a", "b"], client=client(h)).fetch()
    assert len(out) == 1 and appels == ["a", "b"]


def test_cle_refusee():
    with pytest.raises(AdzunaError):
        Adzuna("i", "k", VILLES, ["a"], client=client(lambda r: httpx.Response(401))).fetch()
