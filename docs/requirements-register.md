# Registre de conformité — La Gazelle

Source : `docs/document/La_Gazelle_Cahier_des_charges_site_web.docx` et `docs/document/La_Gazelle_Contenus_complets_site_web.docx`.

Ce registre sépare ce qui est déjà implémenté dans le code de ce qui exige une information ou une recette réelle. Un contenu « fourni dans le document » ne rend pas automatiquement officielles les données que le cahier demande de confirmer.

| ID | Exigence | Implémentation actuelle | État de validation |
|---|---|---|---|
| REQ-F-001 | Accueil de La Gazelle | Accueil restructuré autour de la promesse, des besoins, des huit expertises, de la méthode et des appels à l’action. | Code présent ; recette visuelle à faire |
| REQ-F-002 | Présentation du cabinet | Page « Le cabinet » reprend les textes fournis ; dates et direction non confirmées sont omises. | Texte à relire par La Gazelle |
| REQ-F-003 | Huit expertises du cahier | Huit fiches actives avec besoins, actions, livrables, résultats attendus, SEO et liens croisés. | Code et contenus fournis présents |
| REQ-F-004 | FAQ | Catégories et réponses fournies, filtrage et données structurées. | Code présent ; recette navigateur à faire |
| REQ-F-005 | Conseils et article de lancement | Espace Conseils connecté à la FAQ ; article préparé en brouillon sans auteur/date inventés. | Auteur et date à valider avant publication |
| REQ-F-006 | Réalisations et preuves | Modèles, brouillons et autorisations client pour nom, logo, citation et résultats. | Aucune preuve ne doit être publiée sans accord |
| REQ-F-007 | Équipe | Publication dynamique après validation de l’identité, fonction et droits photo. | Personnes et autorisations à fournir |
| REQ-F-008 | Formulaire de projet | Champs conformes au document, consentement, contact alternatif, référence, anti-spam, enregistrement et notifications rejouables. Pas de nouvel upload. | Fermé jusqu’à publication de la politique de confidentialité ; recette réelle restante |
| REQ-ADM-001 | Administration et brouillons | Gestion des pages, expertises, FAQ, articles, réalisations, équipe et aperçus protégés. | Code présent ; comptes et permissions à configurer |
| REQ-ADM-002 | Suivi commercial | Statuts, historique, états de notification, relance et export limité par permission. | Code présent ; recette avec comptes réels restante |
| REQ-SEC-001 | Protéger les demandes | Accès staff par permission, anti-spam, contrôle des téléchargements historiques et limitation des tentatives admin. | Code présent ; recette proxy et déploiement restante |
| REQ-SEC-002 | Conservation maîtrisée | Durée configurée explicitement ; commande de purge en aperçu par défaut, exécution manuelle explicite. | Durée à définir ; tâche opérationnelle à planifier |
| REQ-SEO-001 | Référencement | Titres, descriptions, canoniques, robots, sitemap et données structurées. Indexation désactivée par défaut ; contrôle de publication disponible. | Domaine et contenu de confiance à valider |
| REQ-UX-001 | Responsive et accessible | CSS responsive, focus visible, formulaires libellés, menu clavier et réduction des animations. | Audit réel de 360 à 1440 px restant |
| REQ-NF-001 | Exploitation et qualité | Paramètres production, Nginx, PostgreSQL, SMTP, cache et procédure de sauvegarde documentés. | Recette réelle et restauration à documenter |

## Informations qui empêchent une publication complète

- Confirmer l’adresse e-mail, le téléphone, WhatsApp, l’adresse du siège et le responsable de publication.
- Vérifier la dénomination, le capital, le RCCM, l’IFU et les coordonnées de l’hébergeur avant publication légale.
- Rédiger et valider la politique de confidentialité : finalités et base légale, destinataires, prestataires, localisation/transferts, données techniques et journaux, cookies, droits, contact et durée de conservation.
- Définir la durée de conservation des demandes et programmer la purge périodique après validation.
- Confirmer les comptes sociaux, les personnes et fonctions de l’équipe, les droits d’image, l’auteur/date de l’article et les accords des cas clients.
- Configurer le domaine, le SMTP, hCaptcha, l’hébergement et le destinataire des notifications.
- Faire la recette mobile/accessibilité/performance, l’essai d’e-mails, la recette CAPTCHA, ainsi qu’une sauvegarde et une restauration.

La commande `python manage.py release_check` vérifie les critères de données et de configuration avant indexation. Elle reste volontairement bloquante tant que ces éléments ne sont pas renseignés et validés.
