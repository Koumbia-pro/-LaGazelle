import csv

from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html

from apps.core.audit import record_audit
from apps.core.admin_mixins import AuditedModelAdmin

from .models import ProjectRequest, ProjectRequestStatusHistory
from .notifications import send_project_notifications


def _spreadsheet_safe(value):
    """Stop spreadsheet applications interpreting user text as a formula."""
    value = "" if value is None else str(value)
    first_content = value.lstrip("\x00\ufeff").lstrip()
    if first_content[:1] in {"=", "+", "-", "@"}:
        return f"'{value}"
    return value


class StatusHistoryInline(admin.TabularInline):
    model = ProjectRequestStatusHistory
    extra = 0
    readonly_fields = ("from_status", "to_status", "changed_by", "created_at")


@admin.register(ProjectRequest)
class ProjectRequestAdmin(AuditedModelAdmin):
    list_display = (
        "reference", "created_at", "full_name", "company", "service", "status",
        "team_notification_status", "visitor_notification_status",
    )
    list_filter = ("status", "team_notification_status", "visitor_notification_status", "created_at")
    search_fields = ("reference", "first_name", "last_name", "company", "email", "phone", "whatsapp", "service")
    readonly_fields = (
        "reference", "created_at", "updated_at", "consent", "attachment_link",
        "team_notification_status", "visitor_notification_status", "notification_error", "last_notification_attempt",
    )
    exclude = ("attachment", "client_type")
    list_per_page = 25
    inlines = [StatusHistoryInline]
    actions = ("retry_failed_notifications", "export_selected_requests")

    @admin.display(description="Nom", ordering="first_name")
    def full_name(self, obj):
        return obj.full_name

    @admin.display(description="Pièce jointe historique")
    def attachment_link(self, obj):
        if not obj or not obj.pk or not obj.attachment:
            return "Aucune pièce jointe"
        return format_html(
            '<a href="{}">Télécharger la pièce jointe ↗</a>',
            reverse("contact:attachment", args=[obj.pk]),
        )

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.has_perm("contact.export_projectrequest"):
            actions.pop("export_selected_requests", None)
        return actions

    @admin.action(description="Réessayer les notifications en échec")
    def retry_failed_notifications(self, request, queryset):
        count = 0
        for project in queryset.filter(team_notification_status="failed") | queryset.filter(visitor_notification_status="failed"):
            send_project_notifications(project)
            count += 1
        self.message_user(request, f"Nouvelle tentative effectuée pour {count} demande(s).")

    @admin.action(description="Exporter les demandes sélectionnées (accès autorisé uniquement)")
    def export_selected_requests(self, request, queryset):
        if not request.user.has_perm("contact.export_projectrequest"):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="demandes-la-gazelle.csv"'
        response.write("\ufeff")
        writer = csv.writer(response)
        writer.writerow(("Référence", "Créée le", "Nom", "Entreprise ou activité", "E-mail", "Téléphone", "WhatsApp", "Besoin", "Message", "Budget", "Échéance", "Statut"))
        for project in queryset.order_by("created_at"):
            writer.writerow(tuple(_spreadsheet_safe(value) for value in (
                project.reference, project.created_at.isoformat(), project.full_name, project.company,
                project.email, project.phone, project.whatsapp, project.service, project.description,
                project.budget, project.deadline, project.get_status_display(),
            )))
        return response

    def save_model(self, request, obj, form, change):
        previous = None
        if change:
            previous = ProjectRequest.objects.get(pk=obj.pk).status
        super(AuditedModelAdmin, self).save_model(request, obj, form, change)
        record_audit(
            action="modification" if change else "création",
            obj=f"Demande {obj.reference}",
            request=request,
        )
        if previous != obj.status:
            ProjectRequestStatusHistory.objects.create(
                request=obj,
                from_status=previous or "",
                to_status=obj.status,
                changed_by=request.user,
            )

    def delete_model(self, request, obj):
        reference = obj.reference
        super(AuditedModelAdmin, self).delete_model(request, obj)
        record_audit(action="suppression", obj=f"Demande {reference}", request=request)

    def delete_queryset(self, request, queryset):
        references = list(queryset.values_list("reference", flat=True))
        super(AuditedModelAdmin, self).delete_queryset(request, queryset)
        for reference in references:
            record_audit(action="suppression", obj=f"Demande {reference}", request=request)
