from jobbot import signaux as sg


def test_contrat_reel():
    assert sg.contrat("Data Analyst Junior en Alternance H/F", "") == "alternance"
    assert sg.contrat("Data Engineer H/F", "CDI") == "cdi"
    assert sg.contrat("Chargé d'Etudes Data Analyste (H/F)-Alternance", "") == "alternance"
    assert sg.contrat("Data Analyst", "", "Contrat d'apprentissage de 24 mois") == "alternance"
    assert sg.contrat("Growth Operations Apprentice", "FullTime") == "alternance"
    assert sg.contrat("Data Analyst", "") == "inconnu"


def test_niveau():
    assert sg.niveau("Senior Data Engineer H/F") == "senior"
    assert sg.niveau("Lead Data Analyst") == "senior"
    assert sg.niveau("Data Analyst H/F", "Vous justifiez de 5 ans d'expérience en BI") == "senior"
    assert sg.niveau("Data Analyst H/F", "Une première expérience est un plus") == "junior"
    assert sg.niveau("Data Analyst Junior") == "junior"
    assert sg.niveau("Data Analyst H/F") == ""


def test_role():
    assert sg.role("Data Analyst Alteryx - Powerbi H/F") == "analyst"
    assert sg.role("Chargé d'Etudes Data Analyste (H/F)-Alternance") == "analyst"
    assert sg.role("Analytics Engineer - Data Engineer H/F") == "analytics_eng"
    assert sg.role("Data Engineer GCP") == "data_eng"
    assert sg.role("Ingénieur Data Confirmé H/F") == "data_eng"
    assert sg.role("Développeur·se Data & IA – Alternance") == "scientist"
    assert sg.role("Senior Software Engineer - Paris") == "dev"
    assert sg.role("Data Officer H/F") == "analyst"
    assert sg.role("Responsable comptable") == "autre"


def test_annees_et_domaines():
    assert sg.annees("Minimum 3 ans d'expérience, idéalement 5 ans d'expérience") == 5
    assert sg.annees("Débutant accepté") is None
    assert "e-commerce" in sg.domaines("Data Analyst", "Kiabi", "retail et e-commerce")


def test_signaux_entree():
    s = sg.signaux({"titre": "Data Analyst Junior en Alternance H/F", "entreprise": "ACME", "contrat": "", "texte": ""})
    assert s == {"contrat": "alternance", "role": "analyst", "niveau": "junior", "domaines": []}
