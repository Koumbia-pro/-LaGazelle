from django.db import migrations


UNVERIFIED_URLS = [
    "https://fr-fr.facebook.com/LaGazellemedia/",
    "https://www.goafricaonline.com/bf/684617-la-gazelle-agence-web-marketing",
    "https://www.gazellecommunication.fr/",
]


def clear_unverified_urls(apps, schema_editor):
    SocialLink = apps.get_model("core", "SocialLink")
    SocialLink.objects.filter(url__in=UNVERIFIED_URLS).update(url="")


class Migration(migrations.Migration):
    dependencies = [("core", "0003_aboutmilestone_qualitypoint_sitemetric_value")]

    operations = [migrations.RunPython(clear_unverified_urls, migrations.RunPython.noop)]
