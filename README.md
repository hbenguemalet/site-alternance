# Site alternance

Page perso (non indexée) qui liste les alternances data / SQL trouvées par le bot.

- `index.html`, `style.css`, `theme.css`, `app.js`, `bot.svg` : la page.
- `offres.js` : les offres, réécrites et poussées ici par le bot.
- `patch-jobs-bot.patch` : ajout à appliquer au bot (`git apply patch-jobs-bot.patch`) : export de `offres.js` + `git push`.

## Brancher le bot (sur le serveur où il tourne)

1. Clone ce dépôt en SSH : `git clone git@github.com:hbenguemalet/site-alternance.git ~/site-alternance`
2. Crée une clé : `ssh-keygen -t ed25519 -f ~/.ssh/site_alternance -N ""`, puis ajoute `site_alternance.pub`
   dans GitHub : dépôt, Settings, Deploy keys, **Allow write access**. Dans `~/.ssh/config` :
   `Host github.com` / `IdentityFile ~/.ssh/site_alternance`.
3. Dans `config.yaml` du bot :
   ```yaml
   site:
     profil: alternance-data
     dossier: /home/ubuntu/site-alternance
     git_push: true
   ```
4. Au prochain passage du bot, `offres.js` est commité et poussé si la liste a changé.

## Publier avec GitHub Pages
Settings, Pages, Source : branche `main`, dossier `/ (root)`. Chaque push du bot republie la page.
