import logging

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger(__name__)


def send_project_notifications(project):
    """Attempt each notification separately and retain enough state to retry it."""
    errors = []
    project.last_notification_attempt = timezone.now()

    try:
        body = "\n".join([
            f"Référence : {project.reference}",
            f"Nom : {project.full_name}",
            f"Entreprise ou activité : {project.company}",
            f"E-mail : {project.email or 'Non renseigné'}",
            f"Téléphone : {project.phone or 'Non renseigné'}",
            f"WhatsApp : {project.whatsapp or 'Non renseigné'}",
            f"Besoin : {project.service}",
            f"Budget : {project.budget or 'Non renseigné'}",
            f"Échéance : {project.deadline or 'Non renseignée'}",
            "",
            project.description,
        ])
        sent = send_mail(
            f"Nouvelle demande {project.reference} — La Gazelle",
            body,
            settings.DEFAULT_FROM_EMAIL,
            [settings.PROJECT_NOTIFICATION_EMAIL],
            fail_silently=False,
        )
        if sent:
            project.team_notification_status = "sent"
        else:
            project.team_notification_status = "failed"
            errors.append("La notification à l’équipe n’a pas été acceptée par le serveur e-mail.")
    except Exception as exc:
        project.team_notification_status = "failed"
        errors.append(f"Équipe : {exc}")
        logger.exception("Team notification failed for project %s", project.reference)

    if not project.email:
        project.visitor_notification_status = "skipped"
    else:
        try:
            sent = send_mail(
                f"Votre demande {project.reference} a bien été reçue — La Gazelle",
                "Merci pour votre message. Votre demande a bien été enregistrée sous la référence "
                f"{project.reference}. L’équipe vous répondra à l’adresse ou au numéro indiqué.",
                settings.DEFAULT_FROM_EMAIL,
                [project.email],
                fail_silently=False,
            )
            if sent:
                project.visitor_notification_status = "sent"
            else:
                project.visitor_notification_status = "failed"
                errors.append("L’accusé de réception au visiteur n’a pas été accepté par le serveur e-mail.")
        except Exception as exc:
            project.visitor_notification_status = "failed"
            errors.append(f"Visiteur : {exc}")
            logger.exception("Visitor acknowledgement failed for project %s", project.reference)

    project.notification_error = "\n".join(errors)[:4000]
    project.save(update_fields=[
        "team_notification_status",
        "visitor_notification_status",
        "notification_error",
        "last_notification_attempt",
        "updated_at",
    ])
    return not errors
