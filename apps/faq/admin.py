from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from apps.core.admin_mixins import AuditedModelAdmin

from .models import FAQCategory, FAQItem


class FAQItemInline(admin.TabularInline):
    model = FAQItem
    extra = 1


@admin.register(FAQCategory)
class FAQCategoryAdmin(AuditedModelAdmin):
    list_display = ("name", "expertise", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [FAQItemInline]
    readonly_fields = ("preview_link",)

    @admin.display(description="Aperçu")
    def preview_link(self, obj):
        if not obj or not obj.pk:
            return "Enregistrez la catégorie pour la prévisualiser."
        return format_html('<a href="{}" target="_blank" rel="noopener">Prévisualiser la FAQ ↗</a>', reverse("faq:preview", args=[obj.pk]))


@admin.register(FAQItem)
class FAQItemAdmin(AuditedModelAdmin):
    list_display = ("question", "category", "order", "is_active")
    list_filter = ("is_active", "category")
    search_fields = ("question", "answer")
