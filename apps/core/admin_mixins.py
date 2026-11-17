from django.contrib import admin

from .audit import record_audit


class AuditedModelAdmin(admin.ModelAdmin):
    """Add a small, consistent audit trail to content managed in Django Admin."""

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        record_audit(
            action="modification" if change else "création",
            obj=obj,
            request=request,
        )

    def delete_model(self, request, obj):
        label = str(obj)
        super().delete_model(request, obj)
        record_audit(action="suppression", obj=label, request=request)

    def delete_queryset(self, request, queryset):
        # Django's bulk delete action bypasses delete_model(), so record each
        # object before deleting it instead of leaving an audit blind spot.
        labels = [str(obj) for obj in queryset]
        super().delete_queryset(request, queryset)
        for label in labels:
            record_audit(action="suppression", obj=label, request=request)
