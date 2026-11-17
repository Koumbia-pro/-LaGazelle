import os
from datetime import date

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import OperationalError

from apps.contact.privacy import INCOMPLETE_MARKERS, PRIVACY_POLICY_SETTING_KEYS
from apps.core.models import SiteSetting, SocialLink
from apps.faq.models import FAQCategory
from apps.pages.models import Page
from apps.services.models import Expertise
from apps.stories.models import Article, CaseStudy


REQUIRED_EXPERTISE_SLUGS = {
    "audit-digital-strategie-marketing",
    "reseaux-sociaux-contenus",
    "digitalisation-pme-solutions-web",
    "e-reputation-communication-crise",
    "personal-branding-dirigeants",
    "lancement-produits-activation",
    "intelligence-artificielle-automatisation",
    "cybersecurite-protection-acces",
}


class Command(BaseCommand):
    help = "Vérifie les exigences techniques et éditoriales avant indexation publique."

    def handle(self, *args, **options):
        issues = []
        database_engine = settings.DATABASES["default"]["ENGINE"]

        if settings.DEBUG:
            issues.append("DEBUG doit être désactivé.")
        if not settings.SECRET_KEY or settings.SECRET_KEY.startswith("django-insecure-") or len(settings.SECRET_KEY) < 50:
            issues.append("SECRET_KEY robuste manquante.")
        if not settings.ALLOWED_HOSTS or "*" in settings.ALLOWED_HOSTS:
            issues.append("ALLOWED_HOSTS doit contenir les domaines publics.")
        if "sqlite" in database_engine:
            issues.append("PostgreSQL (ou une base serveur équivalente) doit être configurée.")
        if settings.EMAIL_BACKEND != "django.core.mail.backends.smtp.EmailBackend" or not settings.EMAIL_HOST:
            issues.append("SMTP de production manquant.")
        if not os.getenv("PROJECT_NOTIFICATION_EMAIL", "").strip():
            issues.append("PROJECT_NOTIFICATION_EMAIL doit être explicitement configuré et validé.")
        if not settings.HCAPTCHA_SITE_KEY or not settings.HCAPTCHA_SECRET_KEY:
            issues.append("Clés hCaptcha manquantes.")
        if not settings.SEARCH_INDEXING_ENABLED:
            issues.append("SEARCH_INDEXING_ENABLED doit être activé uniquement après la recette de préproduction.")

        try:
            required_public_settings = ("site_name", "site_email", "site_phone_standard", "site_whatsapp", "site_location")
            required_validated_settings = (
                "site_legal_name", "site_company_capital", "site_rccm", "site_ifu", "site_address",
                "site_publication_manager", "site_hosting_provider",
            ) + PRIVACY_POLICY_SETTING_KEYS
            required_keys = required_public_settings + required_validated_settings
            values = {
                row["key"]: row
                for row in SiteSetting.objects.filter(key__in=required_keys).values("key", "value", "is_public")
            }
            for key in required_public_settings:
                row = values.get(key)
                if not row or not row["value"].strip():
                    issues.append(f"Paramètre manquant : {key}.")
                elif not row["is_public"]:
                    issues.append(f"Paramètre non validé pour publication : {key}.")
                elif any(marker in row["value"].lower() for marker in (
                    "à confirmer", "a confirmer", "à valider", "a valider", "à configurer", "à définir", "a definir",
                )):
                    issues.append(f"Paramètre non finalisé : {key}.")

            for key in required_validated_settings:
                row = values.get(key)
                if not row or not row["value"].strip():
                    issues.append(f"Information à renseigner et valider : {key}.")
                elif any(marker in row["value"].lower() for marker in ("à confirmer", "a confirmer", "à valider", "a valider", "à définir", "a definir", "à compléter", "a completer")):
                    issues.append(f"Information non validée : {key}.")

            retention = values.get("site_lead_retention_months", {}).get("value", "")
            if retention and (not retention.strip().isdigit() or int(retention) < 1):
                issues.append("site_lead_retention_months doit être un nombre de mois supérieur ou égal à un.")
            notification_recipient = values.get("site_privacy_notification_recipient", {}).get("value", "").lower()
            configured_recipient = settings.PROJECT_NOTIFICATION_EMAIL.strip().lower()
            if notification_recipient and configured_recipient and configured_recipient not in notification_recipient:
                issues.append("Le destinataire de notification doit être mentionné dans la politique de confidentialité.")
            updated_at = values.get("site_privacy_updated_at", {}).get("value", "").strip()
            if updated_at:
                try:
                    date.fromisoformat(updated_at)
                except ValueError:
                    issues.append("site_privacy_updated_at doit être une date ISO (AAAA-MM-JJ).")

            legal_slugs = ("mentions-legales", "politique-de-confidentialite")
            legal_pages = {
                page.slug: page
                for page in Page.objects.filter(slug__in=legal_slugs, status="published")
            }
            for slug in legal_slugs:
                page = legal_pages.get(slug)
                if not page:
                    issues.append(f"Page de confiance publiée manquante : {slug}.")
                    continue
                legal_text = f"{page.intro} {page.content}".lower()
                if any(marker in legal_text for marker in INCOMPLETE_MARKERS):
                    issues.append(f"Page de confiance non finalisée : {slug}.")
                if not page.meta_title.strip() or not page.meta_description.strip():
                    issues.append(f"Métadonnées SEO manquantes pour la page : {slug}.")
                if slug == "mentions-legales":
                    for key in (
                        "site_legal_name", "site_company_capital", "site_rccm", "site_ifu", "site_address",
                        "site_email", "site_phone_standard", "site_publication_manager", "site_hosting_provider",
                    ):
                        value = values.get(key, {}).get("value", "").strip().lower()
                        if value and value not in legal_text:
                            issues.append(f"Les mentions légales doivent inclure la valeur validée de {key}.")
                if slug == "politique-de-confidentialite":
                    for key in PRIVACY_POLICY_SETTING_KEYS:
                        value = values.get(key, {}).get("value", "").strip().lower()
                        if value and value not in legal_text:
                            issues.append(f"La politique de confidentialité doit inclure la valeur validée de {key}.")

            active_slugs = set(Expertise.objects.filter(is_active=True).values_list("slug", flat=True))
            if active_slugs != REQUIRED_EXPERTISE_SLUGS:
                issues.append("Le catalogue publié doit contenir exactement les huit expertises du cahier des charges.")
            for expertise in Expertise.objects.filter(is_active=True):
                for field in ("headline", "audience_need", "activities", "deliverables", "outcomes", "cta_label", "meta_title", "meta_description"):
                    if not getattr(expertise, field).strip():
                        issues.append(f"Contenu ou référencement manquant pour l’expertise {expertise.slug} : {field}.")
            if not FAQCategory.objects.filter(is_active=True, items__is_active=True).exists():
                issues.append("La FAQ doit contenir au moins une catégorie et une question actives.")
            published_articles = Article.objects.filter(status="published", published_at__isnull=False)
            if not any(article.author.strip() for article in published_articles):
                issues.append("Conseils doit publier un article avec un auteur réel et sa date de publication.")

            for case in CaseStudy.objects.filter(status="published"):
                if not case.client_authorized:
                    issues.append(f"Accord de publication manquant pour la réalisation {case.slug}.")
                if case.client_name and not case.client_name_authorized:
                    issues.append(f"Accord de publication du nom manquant pour la réalisation {case.slug}.")
                if case.results and not case.result_method:
                    issues.append(f"Méthode de mesure manquante pour les résultats de {case.slug}.")
                if case.client_logo and not case.client_logo_authorized:
                    issues.append(f"Autorisation de logo manquante pour la réalisation {case.slug}.")
                if case.quote and not case.quote_authorized:
                    issues.append(f"Autorisation de citation manquante pour la réalisation {case.slug}.")

            if SocialLink.objects.filter(is_active=True).filter(url="").exists():
                issues.append("Un réseau social activé n’a pas d’URL officielle.")
        except OperationalError:
            issues.append("La base de données de production est inaccessible.")

        if issues:
            self.stderr.write(self.style.ERROR("Publication/indexation bloquée :"))
            for issue in issues:
                self.stderr.write(f"- {issue}")
            raise CommandError("Corriger les points ci-dessus avant d’activer l’indexation publique.")

        self.stdout.write(self.style.SUCCESS("Contrôle de publication réussi."))
