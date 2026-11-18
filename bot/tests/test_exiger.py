from pathlib import Path

import yaml

from jobbot.filters import evaluate
from jobbot.models import Offer
from jobbot.profiles import load

RACINE = Path(__file__).resolve().parents[1]
VILLES = {"lille", "paris"}


def profil():
    return load(RACINE / "profiles.yaml", VILLES)[0]


def offre(desc="", fiche="", title="Alternance Data & People analytics"):
    return Offer("greenhouse", "1", title, "ACME", "Paris", "https://x/1", desc, contract="alternance",
                 fiche=fiche, city_key="paris")


RH = "Vous accompagnez les équipes RH : reporting, indicateurs de turnover, enquêtes d'engagement, " * 3
TECH = RH + " Maîtrise de SQL et Power BI exigée."


def test_poste_rh_sans_stack_rejete():
    v = evaluate(profil(), offre(fiche=RH))
    assert not v.ok and "stack" in v.raison


def test_stack_dans_annonce_accepte():
    assert evaluate(profil(), offre(fiche=TECH)).ok


def test_sans_texte_pas_de_controle():
    assert evaluate(profil(), offre()).ok  # mail d'alerte : on ne peut pas vérifier
