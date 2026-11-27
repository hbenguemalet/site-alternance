/* Candidatures spontanées : entreprises de la métropole lilloise avec une activité data / BI.
   Données ci-dessous ; l'état « envoyée » reste sur l'appareil (localStorage).
   Bouton « Offres d'emploi » : page trouvée par le bot sur le site de l'entreprise (offres.js,
   `pages_emploi`), sinon `carrieres` ci-dessous ; sans l'une ni l'autre, seul le site web est proposé. */
(function () {
  "use strict";
  var CLE = "alternance-data-2027:spontanees";
  var PROJET = "https://claude.ai/project/01a1e904-56ee-73eb-8e91-44c63cac8d94";
  var LBA = "https://labonnealternance.apprentissage.beta.gouv.fr/recherche-emploi";

  var E = [
    // --- Distribution, e-commerce, retail : les plus gros besoins BI de la métropole ---
    { id: "decathlon", n: "Decathlon", v: "Villeneuve-d'Ascq", s: "Retail", q: "Siège mondial : supply chain, ventes, produit, CRM. Des centaines de profils data.", site: "https://www.decathlon.fr", carrieres: "https://careers.decathlon.com" },
    { id: "leroymerlin", n: "Leroy Merlin", v: "Lesquin", s: "Retail", q: "Data produit, magasin et e-commerce, avec de grosses équipes BI.", site: "https://www.leroymerlin.fr", carrieres: "https://recrutement.leroymerlin.fr" },
    { id: "adeo", n: "ADEO", v: "Ronchin", s: "Retail", q: "Groupe qui fédère Leroy Merlin, Bricoman… : plateforme data commune.", site: "https://www.adeo.com" },
    { id: "auchan", n: "Auchan Retail", v: "Croix", s: "Retail", q: "Données magasins, fidélité, prix et assortiment.", site: "https://www.auchan.fr" },
    { id: "boulanger", n: "Boulanger", v: "Lesquin", s: "Retail", q: "E-commerce et magasins : pilotage des ventes, CRM, stocks.", site: "https://www.boulanger.com" },
    { id: "kiabi", n: "Kiabi", v: "Lezennes / Hem", s: "Retail", q: "Mode : prévision, assortiment, e-commerce. Offres déjà suivies par le bot.", site: "https://www.kiabi.com", carrieres: "https://jobs.smartrecruiters.com/kiabi" },
    { id: "laredoute", n: "La Redoute", v: "Roubaix", s: "Retail", q: "E-commerce mode et maison : analyse client, merchandising.", site: "https://www.laredoute.fr" },
    { id: "norauto", n: "Norauto", v: "Villeneuve-d'Ascq", s: "Retail", q: "Services auto et e-commerce, groupe Mulliez.", site: "https://www.norauto.fr" },
    { id: "castorama", n: "Castorama", v: "Templemars", s: "Retail", q: "Bricolage : ventes magasins et e-commerce.", site: "https://www.castorama.fr" },
    { id: "pimkie", n: "Pimkie", v: "Villeneuve-d'Ascq", s: "Retail", q: "Mode : suivi des ventes et des collections.", site: "https://www.pimkie.fr" },
    // --- Banque, assurance, paiement ---
    { id: "oney", m: "oney", n: "Oney", v: "Villeneuve-d'Ascq", s: "Banque / paiement", q: "Fintech du paiement : scoring, risque, reporting réglementaire.", site: "https://www.oney.fr" },
    { id: "cofidis", n: "Cofidis", v: "Villeneuve-d'Ascq", s: "Banque / paiement", q: "Crédit : données clients, risque, marketing.", site: "https://www.cofidis.fr" },
    { id: "canordfrance", n: "Crédit Agricole Nord de France", v: "Lille", s: "Banque / paiement", q: "Banque régionale : pilotage commercial et risque.", site: "https://www.ca-norddefrance.fr" },
    { id: "ceHdf", n: "Caisse d'Épargne Hauts-de-France", v: "Lille", s: "Banque / paiement", q: "Banque régionale : data client et pilotage.", site: "https://www.caisse-epargne.fr" },
    { id: "bpn", n: "Banque Populaire du Nord", v: "Lille", s: "Banque / paiement", q: "Banque régionale : reporting et marketing.", site: "https://www.banquepopulaire.fr" },
    // --- Tech ---
    { id: "ovh", n: "OVHcloud", v: "Roubaix", s: "Tech", q: "Cloud européen : data engineering, produit, finance.", site: "https://www.ovhcloud.com", carrieres: "https://careers.ovhcloud.com" },
    { id: "ankama", n: "Ankama", v: "Roubaix", s: "Tech", q: "Jeux vidéo : analyse joueurs et monétisation.", site: "https://www.ankama.com", carrieres: "https://www.ankama.com/fr/jobs" },
    { id: "exotec", n: "Exotec", v: "Croix", s: "Tech", q: "Robotique d'entrepôt : data produit et exploitation. Offres suivies par le bot.", site: "https://www.exotec.com", carrieres: "https://apply.workable.com/exotec/" },
    // --- Industrie, agro, énergie ---
    { id: "bonduelle", n: "Bonduelle", v: "Villeneuve-d'Ascq", s: "Industrie / agro", q: "Agro-industrie : planification, qualité, supply chain.", site: "https://www.bonduelle.com" },
    { id: "lesaffre", n: "Lesaffre", v: "Marcq-en-Barœul", s: "Industrie / agro", q: "Levures et fermentation : données de production.", site: "https://www.lesaffre.com" },
    { id: "roquette", n: "Roquette", v: "Lestrem (50 km)", s: "Industrie / agro", q: "Ingrédients végétaux : données industrielles.", site: "https://www.roquette.com" },
    // --- ESN et conseil data : embauchent beaucoup d'alternants ---
    { id: "capgemini", m: "capgemini", n: "Capgemini", v: "Lille", s: "ESN · Conseil", q: "Missions data / BI chez des clients variés.", site: "https://www.capgemini.com/fr-fr" },
    { id: "sopra", m: "sopra", n: "Sopra Steria", v: "Lille", s: "ESN · Conseil", q: "Équipes data et BI à Lille.", site: "https://www.soprasteria.fr" },
    { id: "keyrus", m: "keyrus", n: "Keyrus", v: "Lille", s: "ESN · Conseil", q: "Spécialiste data et BI : Power BI, Qlik, ETL.", site: "https://keyrus.com" },
    { id: "devoteam", m: "devoteam", n: "Devoteam", v: "Lille", s: "ESN · Conseil", q: "Conseil data et cloud.", site: "https://www.devoteam.com/fr" },
    { id: "talan", m: "talan", n: "Talan", v: "Lille", s: "ESN · Conseil", q: "Conseil data, BI et IA.", site: "https://www.talan.com/fr" },
    { id: "onepoint", m: "onepoint", n: "Onepoint", v: "Lille", s: "ESN · Conseil", q: "Conseil et data.", site: "https://www.groupeonepoint.com" },
    { id: "cgi", m: "^cgi", n: "CGI", v: "Lille", s: "ESN · Conseil", q: "Missions BI pour de grands comptes.", site: "https://www.cgi.com/france" },
    { id: "sfeir", n: "SFEIR", v: "Lille", s: "ESN · Conseil", q: "Cabinet tech et data (Google Cloud) : plusieurs offres data à Lille en ce moment.", site: "https://www.sfeir.com", m: "sfeir" },
    { id: "sii", n: "Groupe SII", v: "Lille", s: "ESN · Conseil", q: "ESN avec un pôle data et BI à Lille.", site: "https://www.groupe-sii.com", m: "groupe sii" },
    { id: "astek", n: "Astek", v: "Lille", s: "ESN · Conseil", q: "Ingénierie et data, agence de Lille.", site: "https://astek.net", m: "astek" },
    { id: "inetum", n: "Inetum", v: "Lille", s: "ESN · Conseil", q: "Services numériques : missions data et BI.", site: "https://www.inetum.com/fr", m: "inetum" },
    { id: "ippon", n: "Ippon Technologies", v: "Lille", s: "ESN · Conseil", q: "Conseil data et cloud, agence lilloise.", site: "https://ippon.fr", m: "ippon" },
    { id: "alten", n: "ALTEN", v: "Lille", s: "ESN · Conseil", q: "Ingénierie et conseil, projets data.", site: "https://www.alten.fr", m: "alten" },
    { id: "meritis", n: "Meritis", v: "Lille", s: "ESN · Conseil", q: "Conseil en transformation avec un pôle data.", site: "https://www.meritis.fr", m: "meritis" },
    { id: "scalian", n: "Scalian", v: "Lille", s: "ESN · Conseil", q: "Ingénierie et data.", site: "https://www.scalian.com", m: "scalian" },
    { id: "viveris", n: "Viveris", v: "Lille", s: "ESN · Conseil", q: "Ingénierie des systèmes d'information et data.", site: "https://www.viveris.fr", m: "viveris" },
    { id: "proxiad", n: "Proxiad", v: "Lille", s: "ESN · Conseil", q: "ESN avec des missions data et BI.", site: "https://www.proxiad.com", m: "proxiad" },
    { id: "actimage", n: "Actimage", v: "Lille", s: "ESN · Conseil", q: "Agence digitale et data.", site: "https://www.actimage.com", m: "actimage" },
    { id: "atos", n: "Atos / Eviden", v: "Lille", s: "ESN · Conseil", q: "Services numériques : data et BI.", site: "https://atos.net/fr", m: "atos|eviden" },
    { id: "mantu", n: "Mantu", v: "Lille", s: "ESN · Conseil", q: "Conseil et data.", site: "https://www.mantu.com", m: "mantu" },
    { id: "celad", n: "CELAD", v: "Lille", s: "ESN · Conseil", q: "ESN avec des offres data à Lille.", site: "https://www.celad.com", m: "celad" },
    // --- Startups et écosystème lillois ---
    { id: "sporteasy", n: "SportEasy", v: "Lille", s: "Startup", q: "Application de gestion d'équipes sportives : usage produit, abonnements, croissance.", site: "https://www.sporteasy.net" },
    { id: "cleverconnect", n: "CleverConnect", v: "Lille", s: "Startup", q: "Tech du recrutement : données de campagnes et de candidatures à grande échelle.", site: "https://www.cleverconnect.com" },
    { id: "mobivia", n: "Mobivia", v: "Villeneuve-d'Ascq", s: "Startup", q: "Groupe auto (Norauto, Midas) avec un pôle data et digital qui fonctionne comme une scale-up.", site: "https://www.mobivia.com" },
    { id: "worldline", n: "Worldline", v: "Seclin / Lille", s: "Startup", q: "Paiement : volumes de transactions, détection de fraude, reporting.", site: "https://worldline.com" },
    { id: "euratech", n: "EuraTechnologies", v: "Lille", s: "Écosystème startups", q: "Incubateur de plus de 200 startups : leur annuaire sert de liste pour des candidatures ciblées.", site: "https://www.euratechnologies.com" },
    { id: "plaineimages", n: "Plaine Images", v: "Tourcoing", s: "Écosystème startups", q: "Pôle image et numérique (jeux, médias, animation) : studios et startups à contacter.", site: "https://www.plaine-images.fr" },
    { id: "blanchemaille", n: "Blanchemaille", v: "Roubaix", s: "Écosystème startups", q: "Pôle mode et e-commerce : marques et startups data / retail.", site: "https://www.blanchemaille.com" },
    { id: "lillefrenchtech", n: "Lille French Tech", v: "Lille", s: "Écosystème startups", q: "Communauté des startups de la métropole : annuaire et offres.", site: "https://www.lillefrenchtech.com" },
    // --- Public ---
    { id: "mel", n: "Métropole Européenne de Lille", v: "Lille", s: "Public", q: "Données de territoire, mobilité, open data.", site: "https://www.lillemetropole.fr" },
    { id: "chulille", n: "CHU de Lille", v: "Lille", s: "Public", q: "Données de santé : pilotage et statistiques hospitalières.", site: "https://www.chu-lille.fr" },
    { id: "hdf", n: "Région Hauts-de-France", v: "Lille", s: "Public", q: "Observation et pilotage des politiques régionales.", site: "https://www.hautsdefrance.fr" }
  ];

  var racine = document.getElementById("spontanees");
  if (!racine) return;

  function lire() { try { return JSON.parse(localStorage.getItem(CLE) || "{}"); } catch (e) { return {}; } }
  function ecrire(d) { try { localStorage.setItem(CLE, JSON.stringify(d)); } catch (e) { /* stockage plein ou refusé */ } }
  function el(tag, cls, txt) { var x = document.createElement(tag); if (cls) x.className = cls; if (txt != null) x.textContent = txt; return x; }
  function lien(cls, txt, href) { var a = el("a", cls, txt); a.href = href; a.target = "_blank"; a.rel = "noopener"; return a; }

  function mailType(e) {
    return "Objet : Candidature spontanée · alternance Data / BI (septembre 2027)\n\n"
      + "Bonjour,\n\n"
      + "Je prépare le Master SIAD et je cherche une alternance en data / BI à partir de septembre 2027. "
      + "L'activité de " + e.n + " à " + e.v.split(/[ /]/)[0] + " correspond à ce que je veux faire : [une phrase sur un projet ou un produit de l'entreprise].\n\n"
      + "Je travaille déjà sur [tes outils : SQL, Power BI…] et j'ai réalisé [ton projet le plus proche]. "
      + "Je serais ravi d'échanger 15 minutes pour vous présenter ma démarche.\n\n"
      + "Mon portfolio : https://hbenguemalet.github.io\n\n"
      + "Bien cordialement,\n[Prénom Nom] · [téléphone]";
  }
  function consigne(e) {
    var b = window.BOOTCAMP;
    return "Prépare ma candidature spontanée : un mail court (10 lignes) et une lettre de motivation d'une page pour une alternance data / BI "
      + "à partir de septembre 2027 chez " + e.n + " (" + e.v + ", secteur " + e.s + "). Cherche d'abord ce que fait l'entreprise en data, "
      + "propose une accroche précise, n'invente aucune compétence et signale ce qui manque.\n\nSite : " + e.site
      + (b ? "\n\nAvancée du bootcamp (" + b.pct + " % des notions) : " + b.competences.map(function (c) {
        return c.nom + " : " + (c.acquis.length ? "acquis " + c.acquis.join(", ") : "rien d'acquis") + (c.en_cours.length ? " ; en cours " + c.en_cours.join(", ") : "");
      }).join(" | ") + "." : "");
  }
  function copier(txt, bouton, ok) {
    var fin = function () { var t = bouton.textContent; bouton.textContent = ok; setTimeout(function () { bouton.textContent = t; }, 1600); };
    try { navigator.clipboard.writeText(txt).then(fin, fin); } catch (e) { fin(); }
  }

  // Offres déjà publiées par le bot (offres.js) : quelles entreprises recrutent en data à Lille en ce moment
  var DATA = window.STAGES || {}, toutes = (DATA.meilleures || []).concat(DATA.autres || []);
  var LILLE = /lille|roubaix|tourcoing|villeneuve|marcq|croix\b|lesquin|\b59\b|\(59\)|- 59/i;
  function offresDe(e) {
    var rx = new RegExp(e.m || e.n.toLowerCase().replace(/[^a-z0-9]+/g, ".?"), "i");
    return toutes.filter(function (o) { return rx.test(o.entreprise || "") && LILLE.test(o.lieu || ""); });
  }
  E.forEach(function (e) {
    e.offres = offresDe(e);
    e.alt = e.offres.filter(function (o) { return /alternan|apprenti/i.test((o.contrat || "") + " " + o.titre); });
  });

  var secteur = "", etat = lire();
  var resume = racine.querySelector("summary span"), liste = racine.querySelector(".sp-liste"), pastilles = racine.querySelector(".sp-filtres");

  function maj() {
    var envoyees = E.filter(function (e) { return etat[e.id]; }).length;
    resume.textContent = envoyees + " envoyée" + (envoyees > 1 ? "s" : "") + " sur " + E.length;
    liste.textContent = "";
    var vues = E.filter(function (e) { return !secteur || e.s === secteur; });
    vues.sort(function (a, b) { return (etat[a.id] ? 1 : 0) - (etat[b.id] ? 1 : 0) || (b.alt.length - a.alt.length) || (b.offres.length - a.offres.length); });
    vues.forEach(function (e) {
      var li = el("li", "sp-carte" + (etat[e.id] ? " sp-fait" : ""));
      var tete = el("div", "sp-tete");
      tete.appendChild(el("b", "sp-nom", e.n));
      tete.appendChild(el("span", "a-chip", e.s));
      li.appendChild(tete);
      li.appendChild(el("p", "sp-lieu", e.v));
      li.appendChild(el("p", "sp-pourquoi", e.q));
      if (e.offres.length) {
        var nb = e.alt.length ? e.alt.length + " alternance" + (e.alt.length > 1 ? "s" : "") + " data à Lille" : e.offres.length + " offre" + (e.offres.length > 1 ? "s" : "") + " data à Lille (hors alternance)";
        li.appendChild(lien("a-chip a-chip--good sp-recrute", "● " + nb + " : voir", (e.alt[0] || e.offres[0]).url));
      }
      var act = el("div", "sp-actions");
      // page des offres trouvée par le bot (ou connue) ; sinon on renvoie simplement vers le site de l'entreprise
      var pageEmploi = (DATA.pages_emploi || {})[e.n] || e.carrieres;
      if (pageEmploi) {
        act.appendChild(lien("s-act s-act--voir", "Offres d'emploi ↗", pageEmploi));
        act.appendChild(lien("s-act", "Site web ↗", e.site));
      } else {
        act.appendChild(lien("s-act s-act--voir", "Site web ↗", e.site));
      }
      var ecrit = lien("s-act", "✎ Rédiger avec Claude", PROJET + "?q=" + encodeURIComponent(consigne(e)));
      ecrit.addEventListener("click", function () { try { navigator.clipboard.writeText(consigne(e)); } catch (x) { /* collage manuel */ } });
      act.appendChild(ecrit);
      var q = encodeURIComponent(e.n + " data");
      act.appendChild(lien("s-act", "Offres sur Indeed ↗", "https://fr.indeed.com/jobs?q=" + q + "&l=" + encodeURIComponent(e.v.split(/[ /]/)[0])));
      var mail = el("button", "s-act", "✉ Copier un mail type"); mail.type = "button";
      mail.addEventListener("click", function () { copier(mailType(e), mail, "Copié ✓"); });
      act.appendChild(mail);
      var fait = el("button", "s-act " + (etat[e.id] ? "s-act--oui" : ""), etat[e.id] ? "✓ Envoyée le " + new Date(etat[e.id]).toLocaleDateString("fr-FR") : "J'ai envoyé");
      fait.type = "button";
      fait.addEventListener("click", function () { if (etat[e.id]) delete etat[e.id]; else etat[e.id] = new Date().toISOString(); ecrire(etat); maj(); });
      act.appendChild(fait);
      li.appendChild(act);
      liste.appendChild(li);
    });
  }

  var secteurs = [""].concat(E.map(function (e) { return e.s; }).filter(function (s, i, t) { return t.indexOf(s) === i; }));
  secteurs.forEach(function (s) {
    var b = el("button", "a-chip s-filtre", s || "Tous les secteurs"); b.type = "button";
    b.setAttribute("aria-pressed", s === "");
    b.addEventListener("click", function () {
      secteur = s;
      pastilles.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", x === b); });
      maj();
    });
    pastilles.appendChild(b);
  });
  var aide = racine.querySelector(".sp-lba"); if (aide) aide.href = LBA;
  if (location.hash === "#spontanees") racine.open = true;
  maj();
})();
