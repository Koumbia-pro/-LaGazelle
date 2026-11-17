from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from apps.core.admin_mixins import AuditedModelAdmin

from .models import Article, ArticleSection, CaseStudy


class ArticleSectionInline(admin.StackedInline):
    model = ArticleSection
    extra = 1


@admin.register(Article)
class ArticleAdmin(AuditedModelAdmin):
    list_display = ("title", "category", "author", "published_at", "status", "updated_at")
    list_filter = ("status", "category", "published_at")
    search_fields = ("title", "excerpt", "content", "author")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at", "preview_link")
    inlines = [ArticleSectionInline]

    @admin.display(description="Aperçu")
    def preview_link(self, obj):
        if not obj or not obj.pk:
            return "Enregistrez le brouillon pour le prévisualiser."
        return format_html('<a href="{}" target="_blank" rel="noopener">Prévisualiser l’article ↗</a>', reverse("stories:article-preview", args=[obj.pk]))


@admin.register(CaseStudy)
class CaseStudyAdmin(AuditedModelAdmin):
    list_display = ("title", "client_name", "client_authorized", "status", "updated_at")
    list_filter = ("status", "client_authorized", "client_name_authorized")
    search_fields = ("title", "client_name", "context", "objective", "intervention")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at", "preview_link")

    @admin.display(description="Aperçu")
    def preview_link(self, obj):
        if not obj or not obj.pk:
            return "Enregistrez le brouillon pour le prévisualiser."
        return format_html('<a href="{}" target="_blank" rel="noopener">Prévisualiser la réalisation ↗</a>', reverse("stories:case-preview", args=[obj.pk]))
