"""Signaux d'une offre utiles pour la note de compatibilité affichée sur la page.

Le bot ne note pas lui-même : il extrait des faits de l'annonce (contrat réel, niveau demandé, type de
poste, domaine, années d'expérience) et la page les compare au profil et à l'avancée du bootcamp.
On lit le texte complet quand on l'a ; sinon (alertes e-mail) le titre seul.
"""

import re

from jobbot.contracts import detect
from jobbot.models import Offer

RX_SENIOR_TITRE = re.compile(
    r"\bsenior\b|\bsr\.?\b|confirm[ée]|exp[ée]riment[ée]|\blead\b|\bmanager\b|\bhead\b|principal|architect|\bexpert\b|"
    r"\bcto\b|directeur|responsable", re.I)
RX_JUNIOR = re.compile(
    r"\bjunior\b|\bjr\b|d[ée]butant|jeunes? dipl[oô]m|premi[èe]re exp[ée]rience|sans exp[ée]rience|"
    r"alternan|apprenti|stagiaire|\bintern\b", re.I)
RX_ANNEES = re.compile(r"(\d{1,2})\s*(?:\+|à|a|-)?\s*(?:\d{1,2}\s*)?ans?\s+d['’ ]\s*exp[ée]rience|"
                       r"exp[ée]rience\s+(?:de\s+)?(?:minimum\s+|au moins\s+)?(\d{1,2})\s*ans?", re.I)

# Premier motif qui correspond gagne : l'ordre va du plus proche du métier visé au plus éloigné.
ROLES = [
    ("analyst", r"data ?analy(?:st|ste)|analyste (?:de )?donn[ée]es|analyste (?:bi|d[ée]cisionnel)|bi analyst|"
               r"business (?:&|and)? ?data analy|charg[ée]e? d['’]?[ée]tudes? (?:data|statist)|data officer|reporting|"
               r"data ?(?:&|and) ?analy"),
    ("bi", r"\bbi\b|business intelligence|power ?bi|d[ée]cisionnel"),
    ("analytics_eng", r"analytics engineer|ing[ée]nieur analytics"),
    ("data_eng", r"data ?engineer|ing[ée]nieur(?:\W?e)? data|data ing[ée]nieur|ing[ée]nieur(?:\W?e)? donn[ée]es|"
                 r"data platform|big ?data|data architect|data ?ops|ing[ée]nierie data"),
    ("scientist", r"data ?scien|machine learning|\bml\b|\bia\b|\bai\b|intelligence artificielle"),
    ("dev", r"d[ée]velopp|developer|software|devops|\bsre\b|cloud|platform|fullstack|full stack|architect|\bcto\b|"
            r"engineer|ing[ée]nieur"),
    ("data", r"\bdata\b|donn[ée]es"),
]
RX_ROLES = [(nom, re.compile(motif, re.I)) for nom, motif in ROLES]

DOMAINES = {
    "e-commerce": r"e-?commerce|retail|distribution|magasin|marketplace|catalogue|vente en ligne|merchandising|prestashop|"
                  r"grande distribution|mode\b|beaut[ée]",
    "produit": r"chef de produit|product (?:owner|manager|analyst)|gestion de produits?|donn[ée]es produit|assortiment",
    "marketing": r"marketing|crm|fid[ée]lisation|webanalytics|web analytics|\bseo\b|acquisition|growth",
    "finance": r"banque|assurance|finance|cr[ée]dit|paiement|fintech|actuar",
    "industrie": r"industri|usine|production|supply chain|logisti|[ée]nergie",
    "sante": r"sant[ée]|pharma|h[ôo]pital|m[ée]dical|mutuelle",
    "public": r"minist[èe]re|collectivit|[ée]tat\b|public|radio france|universit",
    "conseil": r"\besn\b|conseil|consulting|cabinet|ssii|services num[ée]riques",
}
RX_DOMAINES = [(nom, re.compile(motif, re.I)) for nom, motif in DOMAINES.items()]


def role(titre: str) -> str:
    for nom, rx in RX_ROLES:
        if rx.search(titre or ""):
            return nom
    return "autre"


def contrat(titre: str, brut: str, texte: str = "") -> str:
    """Contrat réel : le titre et le champ de la source d'abord (comme le bot), le texte si on ne sait pas."""
    c = detect(Offer("site", "0", titre or "", None, "", "", contract=brut or None))
    if c:
        return c
    if re.search(r"\balternan(?:ce|t)|\bapprentissage|contrat pro(?:fessionnalisation)?\b", texte or "", re.I):
        return "alternance"
    return "inconnu"


def annees(texte: str) -> int | None:
    """Plus grand nombre d'années d'expérience demandé dans l'annonce."""
    valeurs = [int(g) for m in RX_ANNEES.finditer(texte or "") for g in m.groups() if g]
    valeurs = [v for v in valeurs if 0 < v <= 20]
    return max(valeurs) if valeurs else None


def niveau(titre: str, texte: str = "") -> str:
    """« senior », « junior » ou « » (rien de précisé)."""
    if RX_SENIOR_TITRE.search(titre or ""):
        return "senior"
    ans = annees(texte)
    if ans is not None and ans >= 3:
        return "senior"
    if RX_JUNIOR.search(titre or "") or RX_JUNIOR.search((texte or "")[:1500]):
        return "junior"
    return ""


def domaines(titre: str, entreprise: str, texte: str = "") -> list[str]:
    base = f"{titre} {entreprise} {(texte or '')[:2500]}"
    return [nom for nom, rx in RX_DOMAINES if rx.search(base)]


def signaux(e: dict) -> dict:
    """Signaux d'une entrée publiée (clés : titre, entreprise, contrat, texte)."""
    texte = e.get("texte", "")
    titre = e.get("titre", "")
    s = {"contrat": contrat(titre, e.get("contrat", ""), texte),
         "role": role(titre),
         "niveau": niveau(titre, texte),
         "domaines": domaines(titre, e.get("entreprise", ""), texte)}
    if (a := annees(texte)) is not None:
        s["annees"] = a
    return s
