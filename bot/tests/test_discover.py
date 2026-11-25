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
