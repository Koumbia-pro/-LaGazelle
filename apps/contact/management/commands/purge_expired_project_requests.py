import calendar

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.core.models import AuditLog, SiteSetting
from apps.contact.models import ProjectRequest


def subtract_months(value, months):
    month_index = value.year * 12 + value.month - 1 - months
    year, zero_based_month = divmod(month_index, 12)
    month = zero_based_month + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


class Command(BaseCommand):
    help = "Prévisualise ou supprime les demandes arrivées à leur durée de conservation validée."

    def add_arguments(self, parser):
        parser.add_argument(
            "--execute",
            action="store_true",
            help="Effectue réellement la suppression. Sans cette option, la commande est en aperçu.",
        )

    def handle(self, *args, **options):
        setting = SiteSetting.objects.filter(key="site_lead_retention_months").first()
        if not setting or not setting.value.strip().isdigit() or int(setting.value) < 1:
            raise CommandError("Renseigner et valider site_lead_retention_months avant toute purge.")

        cutoff = subtract_months(timezone.now(), int(setting.value))
        expired = list(
            ProjectRequest.objects.filter(created_at__lt=cutoff)
            .only("pk", "reference", "first_name", "last_name", "service", "attachment")
        )
        if not options["execute"]:
            self.stdout.write(
                f"Aperçu : {len(expired)} demande(s) atteignent la durée de conservation au {cutoff.date()}. "
                "Aucune donnée supprimée. Relancer avec --execute après validation."
            )
            return

        ids = [project.pk for project in expired]
        attachment_files = [
            (project.attachment.storage, project.attachment.name)
            for project in expired
            if project.attachment
        ]
        with transaction.atomic():
            for project in expired:
                if project.reference:
                    AuditLog.objects.filter(
                        Q(object_repr__startswith=f"{project.reference} — ")
                        | Q(object_repr=f"Demande {project.reference}")
                    ).delete()
            ProjectRequest.objects.filter(pk__in=ids).delete()

        file_errors = 0
        for storage, name in attachment_files:
            try:
                storage.delete(name)
            except Exception:
                file_errors += 1

        self.stdout.write(self.style.SUCCESS(f"{len(ids)} demande(s) expirée(s) supprimée(s)."))
        if file_errors:
            self.stderr.write(
                self.style.WARNING(
                    f"Suppression échouée pour {file_errors} pièce(s) jointe(s) ; vérifier le stockage média."
                )
            )
