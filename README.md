# Site alternance

Page perso (non indexée) qui liste les alternances data / SQL repérées par un bot, mise à jour
toutes les heures par GitHub Actions (pas besoin d'allumer un PC).

- `index.html`, `style.css`, `theme.css`, `app.js`, `bot.svg` : la page.
- `offres.js` : les offres, réécrites par le bot.
- `bot/` : le bot (pages carrières d'entreprises ; alertes e-mail en option). Réglages : `bot/config.yaml`, `bot/profiles.yaml`.
- `.github/workflows/bot.yml` : lance le bot chaque heure, sauvegarde sa mémoire (branche `bot-data`), publie la page.

## Mise en route
1. Settings, Pages, **Source : GitHub Actions**.
2. Onglet Actions, « Bot offres + publication », **Run workflow** (premier lancement).
3. La page est sur `https://hbenguemalet.github.io/site-alternance/`.

## Ajouter les alertes e-mail (optionnel)
Crée une boîte dédiée, mets-y des alertes Indeed / HelloWork / LinkedIn, puis ajoute dans Settings, Secrets and variables, Actions :
`IMAP_HOST`, `IMAP_USER`, `IMAP_PASSWORD`, `IMAP_FOLDER`, et passe `sources.email_alerts` à `true` dans `bot/config.yaml`.

Bot d'origine : jobs-bot de Louis Hanquiez, adapté avec son accord.
