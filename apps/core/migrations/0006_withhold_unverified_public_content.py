from django.db import migrations


def withhold_unverified_content(apps, schema_editor):
    SiteSetting = apps.get_model("core", "SiteSetting")
    SiteSetting.objects.filter(key__in=(
        "site_email", "site_phone", "site_phone_standard", "site_phone_additional",
        "site_whatsapp", "site_address", "site_website", "site_contact_note",
        "site_legal_name", "site_rccm", "site_ifu", "site_tax_info",
    )).update(is_public=False)
    SiteSetting.objects.filter(key="site_email").update(value="hello@lagazelle.media", label="E-mail proposé — à confirmer")
    SiteSetting.objects.filter(key__in=("site_phone", "site_phone_standard")).update(value="+226 25 65 53 95", label="Téléphone proposé — à confirmer")
    SiteSetting.objects.filter(key="site_phone_additional").update(value="", label="Autres téléphones — à confirmer")
    SiteSetting.objects.filter(key="site_whatsapp").update(value="+226 64 09 31 96", label="WhatsApp proposé — à confirmer")
    SiteSetting.objects.filter(key="site_address").update(value="", label="Adresse complète — à confirmer")
    SiteSetting.objects.filter(key="site_contact_note").update(value="Confirmer les coordonnées et les tester avant publication.")

    for model_name in ("SocialLink", "SiteMetric", "AboutMilestone", "Value", "QualityPoint"):
        apps.get_model("core", model_name).objects.all().update(is_active=False)

    apps.get_model("services", "Expertise").objects.all().update(is_active=False)
    apps.get_model("services", "Prestation").objects.all().update(is_active=False)
    apps.get_model("faq", "FAQCategory").objects.all().update(is_active=False)
    apps.get_model("faq", "FAQItem").objects.all().update(is_active=False)
    apps.get_model("team", "TeamMember").objects.all().update(is_verified=False)

    Page = apps.get_model("pages", "Page")
    Page.objects.filter(slug__in=("a-propos", "mentions-legales", "politique-de-confidentialite")).update(status="draft")

    ProjectRequest = apps.get_model("contact", "ProjectRequest")
    ProjectRequest.objects.filter(status__in=("qualifying",)).update(status="in_progress")
    ProjectRequest.objects.filter(status__in=("answered", "converted", "archived")).update(status="treated")
    ProjectRequest.objects.all().update(
        team_notification_status="unknown",
        visitor_notification_status="unknown",
    )

    History = apps.get_model("contact", "ProjectRequestStatusHistory")
    History.objects.filter(to_status="qualifying").update(to_status="in_progress")
    History.objects.filter(to_status__in=("answered", "converted", "archived")).update(to_status="treated")
    History.objects.filter(from_status="qualifying").update(from_status="in_progress")
    History.objects.filter(from_status__in=("answered", "converted", "archived")).update(from_status="treated")


class Migration(migrations.Migration):
    dependencies = [
        ("contact", "0004_alter_projectrequest_team_notification_status_and_more"),
        ("core", "0005_analyticsevent"),
        ("faq", "0002_faqcategory_expertise"),
        ("pages", "0002_page_image_page_image_alt"),
        ("services", "0004_expertise_cta_label_expertise_headline"),
        ("stories", "0002_casestudy_client_logo_casestudy_client_logo_alt_and_more"),
        ("team", "0004_teammember_photo_alt"),
    ]

    operations = [migrations.RunPython(withhold_unverified_content, migrations.RunPython.noop)]
