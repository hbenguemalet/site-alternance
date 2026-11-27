import json

import httpx

from jobbot.sources.discover import decouvrir, detecter


def test_detecter_les_outils():
    assert detecter('<a href="https://jobs.lever.co/acme/123">') == ("lever", "acme")
    assert detecter('<a href="https://boards.greenhouse.io/embed/job_board?for=acme">') == ("greenhouse", "acme")
    assert detecter('<a href="https://acme.recruitee.com/o/x">') == ("recruitee", "acme")
    assert detecter('<a href="https://jobs.ashbyhq.com/acme">') == ("ashby", "acme")
    assert detecter("<p>rien</p>") is None


def test_decouvrir_met_en_cache(tmp_path):
    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.host == "acme.fr" and req.url.path == "/carrieres":
            return httpx.Response(200, text='<a href="https://jobs.lever.co/acme">offres</a>')
        return httpx.Response(404)
    c = httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=True)
    cache = tmp_path / "c.json"
    ents = [{"nom": "Acme", "url": "https://acme.fr"}, {"nom": "Rien", "url": "https://rien.fr"}]
    out = decouvrir(ents, cache, [], c)
    assert out == [{"nom": "Acme", "ats": "lever", "id": "acme"}]
    assert json.loads(cache.read_text())["Rien"]["ats"] is None
    # déjà connue : pas de doublon
    assert decouvrir(ents, cache, out, c) == []


def test_lien_carrieres_et_page():
    from jobbot.sources.discover import lien_carrieres
    html = '<a href="/actu">Actualités</a><a href="https://linkedin.com/jobs">LinkedIn</a><a href="/rejoindre">Carrières</a>'
    assert lien_carrieres(html, "https://acme.fr/") == "https://acme.fr/rejoindre"
    assert lien_carrieres('<a href="/x">Emploi</a>', "https://acme.fr") == "https://acme.fr/x"
    assert lien_carrieres("<p>rien</p>", "https://acme.fr") is None


def test_decouvrir_garde_la_page_meme_sans_outil(tmp_path):
    def h(req):
        if req.url.path == "/":
            return httpx.Response(200, text='<a href="/jobs-chez-nous">Nous rejoindre</a>')
        return httpx.Response(404)
    c = httpx.Client(transport=httpx.MockTransport(h), follow_redirects=True)
    cache = tmp_path / "c.json"
    assert decouvrir([{"nom": "Acme", "url": "https://acme.fr"}], cache, [], c) == []
    from jobbot.sources.discover import pages
    assert pages(cache) == {"Acme": "https://acme.fr/jobs-chez-nous"}


def test_lien_carrieres_ecarte_les_pages_hors_sujet():
    from jobbot.sources.discover import lien_carrieres
    html = '<a href="/assurance-chomage-emploi">Emploi</a><a href="/espace-societaire">Carrières</a><a href="/recrute">Carrières</a>'
    assert lien_carrieres(html, "https://acme.fr") == "https://acme.fr/recrute"
