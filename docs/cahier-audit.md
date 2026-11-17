# Audit de conformité — La Gazelle

Audit du 16 novembre 2026 à partir des deux documents Word fournis dans `docs/document` et du code de l’application.

## Décisions d’interprétation

Le contenu fourni sert de référence pour les textes publics. Les éléments explicitement laissés à confirmer dans les documents — coordonnées, informations juridiques, personnes, preuves clients et autorisations — ne sont pas affichés comme s’ils étaient vérifiés. Les dates de création contradictoires, les résultats clients non démontrés et les profils d’équipe historiques ne sont pas repris.

## État par partie

| Partie | État actuel |
|---|---|
| Logo | Le fichier `logo.png` fourni est utilisé dans l’en-tête, le pied de page et les métadonnées ; `emblem.png` sert de favicon. Les fichiers source ne sont pas altérés. |
| Accueil | Contenu reconstruit selon le document : promesse, besoins clients, expertises, méthode, présentation du cabinet et CTA. Les chiffres et preuves non validés sont retirés. |
| Cabinet | Texte fourni intégré sans inventer de date de création, de directeur ou de rattachement de groupe. |
| Expertises | Catalogue remplacé par les huit expertises du cahier, avec leurs textes complets, livrables, résultats attendus, précautions et métadonnées. Les anciennes prestations hors périmètre sont masquées, pas supprimées. |
| FAQ / Conseils | FAQ alimentée avec les réponses fournies. L’article de lancement est conservé en brouillon tant que l’auteur et la date ne sont pas confirmés. |
| Réalisations | Modèle et pages prêts, mais seules des références publiées avec autorisations explicites sont visibles. Aucune preuve proposée non vérifiée n’est publiée. |
| Équipe | Affichage réservé aux profils vérifiés. Les noms, fonctions, photos et certifications non confirmés ne sont pas inventés ; la présentation de la direction reste à fournir. |
| Formulaire | Champs alignés sur le document, au moins un contact requis, consentement, référence et notification. Pas de téléversement pour les nouvelles demandes. La collecte est fermée tant que la politique de confidentialité n’est pas publiée. |
| Données personnelles | Politique brouillon et coordonnées privées par défaut. La purge des demandes expirées est disponible en mode aperçu et requiert `--execute` pour supprimer. |
| Administration | Modèles administrables, aperçus privés, rôles, historique de statut et suivi/relance des notifications. Les demandes existantes ne sont pas supprimées par le chargement des contenus. |
| SEO | Métadonnées et sitemap dynamiques ; les pages brouillon et contenus non autorisés sont exclus. `robots.txt` désactive l’indexation tant que la recette n’est pas prête. |
| Sécurité | hCaptcha production, aperçus autorisés par permission, formulaires/demandes non cachés, téléchargements staff, images CMS limitées et validées, exports CSV protégés contre les formules, limites de débit et paramètres de production. |
| UX / performance | Interface responsive, clavier, focus visible et réduction des animations prévus dans les styles et scripts. Mesures réelles Lighthouse, poids et accessibilité restent à faire. |

## Comparaison page par page avec les maquettes

| Page | Correspondance | Différence ou condition constatée |
|---|---|---|
| Accueil | Même emblème, hero Gazelle, huit cartes d’expertise, méthode et bannière de contact avec la photo et le message de la nouvelle maquette. | La grille des besoins s’ajoute conformément au cahier. La preuve clients et les réseaux restent cachés sans validation. |
| Expertises | Hero Gazelle, huit cartes, raccourcis par priorité et CTA sombre suivent la maquette orange. | Le lien global Réalisations mène à un état vide tant qu’aucun cas autorisé n’est publié. |
| Le cabinet | Image du bureau, trois rôles, principes, engagements, compétences et CTA reprennent la maquette fournie. | Le bloc mission/ambition conserve le texte du cahier et ajoute une section qui n’apparaît pas dans la capture. |
| Conseils | Hero du bureau, quatre raccourcis, carte éditoriale, FAQ et CTA suivent la structure de la maquette. | Faute d’article publié avec auteur et date confirmés, la carte éditoriale présente une question fréquente avec le visuel fourni. |
| Fiche expertise et réponse FAQ | Gabarits cohérents avec la charte et les fiches de contenu administrables. | Aucune capture spécifique n’a été fournie pour ces détails. |
| Contact | Gabarit de formulaire réactif avec consentement, erreurs et confirmation de référence. | La route répond `503` tant que la politique de confidentialité complète n’est pas publiée. |
| Réalisations | Le lien de navigation et la page restent disponibles ; un état vide explique la règle d’autorisation. | Aucun cas n’est publié sans accord client ; la page vide est `noindex` et n’entre pas dans le sitemap. |
| Équipe | Gabarit de liste et profils administrables. | Sans membre vérifié, la route revient au cabinet ; aucune identité non confirmée n’est affichée. |
| Mentions légales et confidentialité | Les liens du footer restent visibles ; les pages publiées affichent leur contenu éditable et les pages en attente affichent un état explicite `noindex`. | Les pages restent à compléter avec les informations juridiques et de confidentialité validées ; le formulaire reste fermé jusqu’à la publication de la politique complète. |
| FAQ, catalogue de prestations, administration | Écrans disponibles et styles dédiés/responsifs ; la route Prestations redirige vers Expertises. | Aucune maquette indépendante fournie pour ces écrans. |

## Vérifications effectuées dans cette mise à jour

Les tests automatisés passent (28 tests). `python manage.py check` et `makemigrations --check --dry-run` ne signalent aucun problème. `check --deploy`, exécuté avec des variables de démonstration et une configuration PostgreSQL de contrôle, ne signale aucun problème de configuration. Les pages servies par Django ne contiennent aucune image statique manquante.

Les routes publiques sont disponibles pour l’accueil, les expertises, le cabinet, les conseils, la FAQ et les réalisations. Le formulaire renvoie volontairement `503` tant que la politique reste en brouillon ; la page Réalisations affiche un état vide non indexé, et l’équipe revient au cabinet tant qu’aucun profil n’est vérifié. `release_check` bloque donc correctement la mise en ligne indexable.

Les pages Accueil, Expertises, Cabinet et Conseils reprennent la structure et les images des maquettes, avec adaptations pour conserver les exigences du cahier. L’accueil garde sa grille « Choisissez votre point de départ ». Conseils affiche la FAQ tant qu’aucun article n’a d’auteur et de date confirmés. Les coordonnées, les réseaux sociaux, les réalisations et les profils non vérifiés restent masqués.

La recette visuelle dans un navigateur n’a pas pu être terminée dans cet environnement : Chrome headless s’est arrêté avec le code 133 et Firefox avec le code 139. La validation réelle sur mobile, clavier, accessibilité et performance reste à faire. L’environnement virtuel local possède encore Django 5.2.17, Pillow 11.3.0, Gunicorn 23.0.0 et Psycopg 3.3.6 ; `requirements.txt` demande maintenant des versions corrigées plus récentes, à installer avant le déploiement. La migration des validateurs d’images est générée, mais doit être appliquée sur l’environnement cible.

## Éléments restant à confirmer par La Gazelle

1. Coordonnées de contact et siège social.
2. Informations légales exactes, responsable de publication et hébergeur.
3. Fondements, prestataires, localisation, transferts, journaux, cookies, droits et durée de conservation à inscrire dans la politique de confidentialité.
4. Comptes sociaux officiels et destinataire des notifications.
5. Noms, rôles, biographies et autorisations de photos de l’équipe.
6. Auteur et date de publication de l’article ; autorisations et méthode pour toute réalisation client.
7. Compétences et périmètres réellement disponibles pour les interventions IA et cybersécurité.
8. Domaine, SMTP, hCaptcha, recette mobile/accessibilité/performance et essai de restauration.

La mise en ligne indexable n’est pas prête tant que ces informations et contrôles ne sont pas terminés. `python manage.py release_check` fournit la liste des éléments bloquants au moment du déploiement.
