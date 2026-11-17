# La Gazelle — plateforme digitale

Site Django server-rendered réalisé à partir du cahier des charges et du document de contenus de La Gazelle.
Le logo et l’emblème officiels fournis dans `docs/document` sont utilisés dans le site et l’administration.

## Ce que le site comprend

- Accueil, présentation du cabinet et huit expertises avec leurs pages détaillées.
- FAQ, espace Conseils et sections Réalisations, qui n’affichent que les contenus publiés et autorisés.
- Formulaire de projet avec référence, validation, consentement, anti-spam, historique et notifications rejouables.
- Administration des contenus, des demandes et des autorisations de publication, avec rôles et journal d’audit.
- Titres SEO, URL canoniques, sitemap et indexation désactivée par défaut.
- Mesure limitée des conversions, activée seulement après le choix du visiteur.
- Interface responsive, navigation clavier et prise en compte de la réduction des animations.

Les coordonnées, pages légales, profils d’équipe, réseaux sociaux et références client non confirmés restent masqués ou en brouillon. Le formulaire ne collecte aucune donnée tant que la politique de confidentialité n’est pas publiée. Les demandes déjà enregistrées ne sont pas supprimées par `seed_demo`.

## Installation locale

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
set -a
source .env
set +a
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

Le site est disponible sur `http://127.0.0.1:8000/` et l’administration sur `/admin/`. Le fichier `.env.example` est réservé au développement local. Il n’est pas chargé automatiquement : les commandes `set -a` et `source .env` exportent ses paramètres dans le shell.

Après `seed_demo`, les pages de confiance restent en brouillon et le formulaire de projet est fermé jusqu’à leur validation. C’est le comportement attendu tant que les informations juridiques et la conservation des demandes ne sont pas confirmées.

## Contenus et rôles

La commande `python manage.py seed_demo` charge les huit expertises et les textes de référence, prépare une FAQ, crée un article en brouillon et réserve les pages de confiance en brouillon. Elle désactive les anciennes expertises, comptes sociaux et contenus non vérifiés sans supprimer les demandes commerciales. Elle crée les groupes `Administrateur contenu`, `Commercial / projet`, `Éditeur` et `Lecteur` ; affecter les comptes aux groupes depuis l’administration.

Dans l’administration, prévisualiser un contenu puis vérifier les textes, les images et les autorisations avant de le publier. Les coordonnées doivent être marquées publiques seulement après validation.

## Contrôles

```bash
python manage.py check
python manage.py release_check
```

`release_check` est un contrôle de publication : en développement, il doit bloquer la mise en ligne tant que les données légales, les coordonnées, les politiques, les autorisations et l’environnement de production ne sont pas finalisés. Une recette navigateur, mobile, e-mail, CAPTCHA, sauvegarde et restauration reste nécessaire avant l’ouverture publique.

## Production

Utiliser `config.settings.production`, Python 3.12+, Gunicorn derrière Nginx, HTTPS, PostgreSQL, un cache partagé et un SMTP configuré. Les variables de production doivent être fournies par l’environnement du serveur, pas copiées depuis `.env.example`. Garder `SEARCH_INDEXING_ENABLED=False` jusqu’à la recette finale et au passage réussi de `release_check`.

Voir [le guide de déploiement](DEPLOYMENT.md), [l’audit du cahier des charges](docs/cahier-audit.md), [le registre des exigences](docs/requirements-register.md) et [le guide administrateur](docs/admin-guide.md).
