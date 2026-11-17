from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from apps.core.admin_mixins import AuditedModelAdmin

from .models import Expertise, Prestation


class PrestationInline(admin.TabularInline):
    model = Prestation
    extra = 1
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Expertise)
class ExpertiseAdmin(AuditedModelAdmin):
    list_display = ("name", "order", "is_active", "accent_color")
    list_filter = ("is_active",)
    search_fields = ("name", "summary", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [PrestationInline]
    readonly_fields = ("preview_link",)

    @admin.display(description="Aperçu")
    def preview_link(self, obj):
        if not obj or not obj.pk:
            return "Enregistrez l’expertise pour la prévisualiser."
        return format_html('<a href="{}" target="_blank" rel="noopener">Prévisualiser la fiche ↗</a>', reverse("expertises:preview", args=[obj.pk]))


@admin.register(Prestation)
class PrestationAdmin(AuditedModelAdmin):
    list_display = ("name", "expertise", "order", "is_active")
    list_filter = ("is_active", "expertise")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
