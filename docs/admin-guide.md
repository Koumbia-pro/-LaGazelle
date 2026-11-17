# Guide administrateur — La Gazelle

## Accès et rôles

L’administration se trouve sur `/admin/`. Utiliser un compte nominatif et limiter les droits au rôle nécessaire. La commande `python manage.py seed_demo` crée les groupes suivants ; les comptes doivent être affectés depuis l’administration :

- `Administrateur contenu` : administration des contenus et des demandes ;
- `Commercial / projet` : consultation et traitement des demandes, avec export autorisé ;
- `Éditeur` : création et modification des contenus, sans permission de suppression ;
- `Lecteur` : consultation des contenus.

Ne pas partager le compte superutilisateur. Les demandes et exports contiennent des données personnelles.

## Publier une page ou un contenu

1. Ouvrir la fiche dans l’administration et vérifier son titre, son texte et ses métadonnées.
2. Ajouter une image seulement si elle est autorisée et renseigner son texte alternatif.
3. Enregistrer en brouillon, puis ouvrir l’aperçu privé.
4. Vérifier le rendu mobile et les liens.
5. Passer en publié après validation éditoriale et des droits.

Pour une réalisation, confirmer l’autorisation du client, et séparément celles de son nom, logo et citation. Décrire la méthode pour tout résultat chiffré. Pour un profil d’équipe, valider le nom, la fonction et les droits de l’image avant d’activer `is_verified`.

Les liens sociaux sont désactivés tant que leurs URLs officielles ne sont pas confirmées. Les anciens chiffres, jalons et coordonnées proposés restent masqués.

## Coordonnées et pages de confiance

Les paramètres de coordonnées, d’identité juridique, d’hébergement et de confidentialité sont privés ou incomplets par défaut. Vérifier chaque information à partir d’une source officielle avant de la rendre publique.

Les pages Mentions légales et Confidentialité doivent être complètes et publiées avant l’ouverture du formulaire. La politique doit préciser les finalités, bases légales, prestataires, localisation/transferts, données techniques, cookies, droits et durée de conservation. `python manage.py release_check` vérifie ces données, leur présence dans les pages et la configuration de production.

## Demandes de projet

Une demande reçue apparaît dans `Demandes de projet` avec une référence. Les statuts disponibles sont `Nouvelle`, `En cours` et `Traitée`. Les changements sont consignés dans l’historique. Les états d’envoi des notifications sont visibles ; l’action d’administration permet de réessayer les notifications en échec.

Les demandes se collectent uniquement lorsque la politique de confidentialité est publiée. Le nouveau formulaire ne permet pas de joindre un fichier. Les pièces jointes d’anciennes demandes sont téléchargeables depuis le lien protégé de l’administration et ne doivent jamais être partagées par URL publique.

Quand la durée de conservation validée est configurée, prévisualiser les demandes arrivées à échéance avec :

```bash
python manage.py purge_expired_project_requests
```

Après vérification et validation, ajouter `--execute` pour supprimer ces demandes, leur historique et leurs pièces jointes éventuelles. Ne pas exécuter cette suppression avant la validation de la durée applicable.

## Avant la publication

- confirmer les coordonnées, informations légales, domaine et hébergeur ;
- configurer le SMTP, hCaptcha et le destinataire de notification ;
- finaliser les pages de confiance et la conservation des demandes ;
- vérifier les autorisations des personnes et des cas clients ;
- effectuer les recettes réelles mobile, accessibilité, formulaire, emails, CAPTCHA, sauvegarde et restauration ;
- activer `SEARCH_INDEXING_ENABLED` seulement après le passage réussi de `release_check`.
