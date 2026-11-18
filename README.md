# Site alternance

Page perso (privée, non indexée) qui liste les alternances data / SQL trouvées par le bot `jobs-bot`.

- `index.html`, `style.css`, `app.js`, `bot.svg` : la page (réutilise `/kit/kit.css` du site).
- `offres.js` : données, réécrites par le bot à chaque passage.
- `jobs-bot-site.patch` : ajout à appliquer dans le dépôt `jobs-bot` (`git apply`) pour générer `offres.js`.
