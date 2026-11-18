# Déploiement — La Gazelle

## Préparer l’environnement

1. Installer Python 3.12+, PostgreSQL, Nginx et un serveur SMTP.
2. Récupérer le dépôt et créer un environnement virtuel.
3. Installer `requirements.txt`.
4. Fournir les variables d’environnement de production : `DJANGO_SETTINGS_MODULE=config.settings.production`, une `SECRET_KEY` aléatoire d’au moins 50 caractères, `ALLOWED_HOSTS`, la base PostgreSQL, le SMTP, `PROJECT_NOTIFICATION_EMAIL`, les deux clés hCaptcha et un cache partagé.
5. Configurer les coordonnées, l’identité juridique, l’hébergeur, les pages de confiance et les autres informations validées dans l’administration. Ne pas reprendre les valeurs proposées comme des faits confirmés.
6. Exécuter `python manage.py migrate`, puis `python manage.py seed_demo` lors de la première installation.
7. Créer un compte nominatif avec `python manage.py createsuperuser` et affecter les rôles appropriés.
8. Exécuter `python manage.py createcachetable django_cache` si le cache de base de données est utilisé.
9. Exécuter `python manage.py collectstatic --noinput`, lancer Gunicorn avec `config.wsgi:application` et configurer Nginx en HTTPS.
10. Garder l’indexation désactivée pendant la recette. Une fois tous les éléments de la liste ci-dessous confirmés, régler `SEARCH_INDEXING_ENABLED=True`, puis exécuter `python manage.py check --deploy` et `python manage.py release_check`.

Des modèles Nginx et systemd sont disponibles dans `deploy/nginx.conf.example` et `deploy/la-gazelle.service.example`. Remplacer les domaines et chemins de démonstration avant le lancement.

## Conditions d’ouverture

`release_check` bloque la publication si les coordonnées ou mentions légales sont incomplètes, si la politique de confidentialité ne détaille pas les traitements, prestataires, transferts, données techniques, cookies, destinataires et durée de conservation, ou si les contenus et droits de publication ne sont pas validés. L’indexation reste désactivée tant que la recette n’est pas terminée.

Le formulaire de projet demeure fermé tant que la politique de confidentialité n’est pas publiée. Les coordonnées proposées, profils non vérifiés, articles sans auteur/date et cas clients sans autorisation ne sont pas publiés automatiquement.

## Demandes et durée de conservation

Les nouvelles soumissions ne comportent pas de pièce jointe. L’administration conserve néanmoins la prise en charge sécurisée des pièces jointes des anciennes demandes. Nginx doit interdire l’accès direct au répertoire média :

```nginx
location ^~ /media/project-requests/ {
    deny all;
    return 404;
}
```

La route de téléchargement historique passe par Django et exige un compte autorisé. Elle se trouve sous `/contact/<id>/piece-jointe/`.

Après avoir validé `site_lead_retention_months` et l’avoir publié dans la politique de confidentialité, planifier régulièrement un aperçu de la purge :

```bash
python manage.py purge_expired_project_requests
```

La commande n’efface rien sans option explicite. Après vérification et validation par le responsable, ajouter `--execute` pour supprimer les demandes arrivées à échéance, leur historique rattaché, leurs traces d’audit nominatives et leurs pièces jointes éventuelles. Ne pas activer cette tâche avant d’avoir déterminé la durée applicable.

## Recette et sécurité

Avant l’indexation, vérifier sur des appareils réels l’accueil, une fiche expertise, le menu mobile, les erreurs du formulaire, les liens téléphone/e-mail/WhatsApp, le consentement, les deux notifications, hCaptcha, les aperçus privés et les permissions de l’administration. Effectuer et documenter une sauvegarde puis une restauration sur un environnement séparé. Contrôler la performance et l’accessibilité sur plusieurs largeurs d’écran.

Ajouter à Nginx une limitation des tentatives sur `/admin/login/`, en complément des protections applicatives. Transmettre `X-Real-IP` uniquement depuis le proxy de confiance configuré. Les journaux serveur et les sauvegardes doivent suivre la politique de conservation applicable.

## Maintenance

Avant une mise à jour, sauvegarder la base et les médias, déployer les migrations, collecter les fichiers statiques et redémarrer Gunicorn. Vérifier le résultat, puis garder la sauvegarde précédente disponible selon la procédure de restauration du serveur.

## Déploiement sur o2switch avec cPanel

o2switch utilise `Setup Python App` et Passenger pour relier une application Python à un domaine. Le dépôt GitHub peut être cloné avec `Git Version Control`, puis mis à jour depuis l’onglet `Pull or Deploy`.

1. Dans cPanel, créer le domaine `lagazelle.media` et vérifier qu’il pointe vers o2switch.
2. Dans `Git Version Control`, cloner `https://github.com/Koumbia-pro/-LaGazelle.git` dans un dossier privé à la racine du compte, par exemple `/home/COMPTE/lagazelle-app`. Pour un dépôt GitHub privé, configurer une clé SSH avant le clonage.
3. Dans `Setup Python App`, choisir Python 3.12, le même `Application Root`, l’URL `https://lagazelle.media`, le fichier de démarrage `config/wsgi.py` et le point d’entrée `application`.
4. Créer une base MariaDB et un utilisateur dans `MySQL Databases`, puis installer `requirements.txt` dans l’environnement Python. Le projet utilise PyMySQL, un pilote Python pur qui ne nécessite pas `gcc`. Pour Django 5.2, utiliser `DB_ENGINE=django.db.backends.mysql`, `DB_HOST=localhost`, ainsi que les identifiants créés dans cPanel.
5. Définir les variables de production dans `Setup Python App`, notamment `DJANGO_SETTINGS_MODULE=config.settings.production`, `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS=lagazelle.media,www.lagazelle.media`, `CSRF_TRUSTED_ORIGINS=https://lagazelle.media,https://www.lagazelle.media`, le SMTP, hCaptcha et `PROJECT_NOTIFICATION_EMAIL`.
6. Définir `MEDIA_ROOT` vers un dossier du document root du domaine, par exemple `/home/COMPTE/lagazelle.media/media`, afin qu’Apache puisse servir les images publiques. Ne jamais placer le code source dans ce document root. Le sous-dossier `media/project-requests/` doit rester interdit par la configuration Apache/cPanel.
7. Dans le terminal cPanel, depuis l’`Application Root`, exécuter `python manage.py migrate`, `python manage.py seed_demo`, `python manage.py createcachetable django_cache`, `python manage.py collectstatic --noinput`, puis créer le compte avec `python manage.py createsuperuser`.
8. Activer le certificat Let’s Encrypt pour `lagazelle.media` et `www.lagazelle.media`, redémarrer l’application Python, puis vérifier le site, l’administration, les e-mails, hCaptcha et les médias avant d’activer l’indexation.

Pour les mises à jour, utiliser `Update from Remote`, relancer les migrations si nécessaire, exécuter `collectstatic --noinput` et redémarrer l’application dans `Setup Python App`.
