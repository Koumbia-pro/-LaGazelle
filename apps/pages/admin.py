from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from apps.core.admin_mixins import AuditedModelAdmin

from .models import Page


@admin.register(Page)
class PageAdmin(AuditedModelAdmin):
    list_display = ("title", "slug", "status", "updated_at")
    list_filter = ("status",)
    search_fields = ("title", "intro", "content")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("updated_at", "preview_link")

    @admin.display(description="Aperçu")
    def preview_link(self, obj):
        if not obj or not obj.pk:
            return "Enregistrez la page pour la prévisualiser."
        return format_html('<a href="{}" target="_blank" rel="noopener">Prévisualiser la page ↗</a>', reverse("pages:page-preview", args=[obj.pk]))
