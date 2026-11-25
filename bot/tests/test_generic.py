from jobbot.sources.email_alerts import route_for
from jobbot.sources.email_alerts.generic import PARSERS
from jobbot.sources.francetravail import to_offer

HTML = """<table><tr><td>
<a href="https://track.x/c?url=https%3A%2F%2Fwww.welcometothejungle.com%2Ffr%2Fcompanies%2Facme%2Fjobs%2Fdata-analyst-alternance_lille&u=1">Data Analyst en alternance</a>
<p>Acme</p><p>Lille</p></td></tr>
<tr><td><a href="https://track.x/opaque/abc123">Un lien de suivi opaque</a><p>X</p><p>Y</p></td></tr></table>"""


def test_wttj_deballe_le_lien_et_ignore_le_suivi():
    offres = PARSERS["wttj"][1](HTML)
    assert len(offres) == 1
    o = offres[0]
    assert o.title == "Data Analyst en alternance" and o.company == "Acme" and o.location == "Lille"
    assert o.url.startswith("https://www.welcometothejungle.com/fr/companies/acme/jobs/")


def test_routes_pour_les_nouveaux_sites():
    for dom in ("welcometothejungle.com", "jooble.org", "adzuna.fr", "apec.fr", "francetravail.fr"):
        assert route_for(f"alertes@{dom}") is not None


def test_france_travail_to_offer():
    o = to_offer({"id": "123ABC", "intitule": "Alternant BI", "entreprise": {"nom": "Foo"},
                  "lieuTravail": {"libelle": "59 - Lille"}}, "lille")
    assert o.source_id == "123ABC" and o.url.endswith("/detail/123ABC") and o.contract == "alternance"
