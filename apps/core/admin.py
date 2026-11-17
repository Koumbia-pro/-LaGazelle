from django.contrib import admin

from .admin_mixins import AuditedModelAdmin
from .models import AnalyticsEvent, AboutMilestone, AuditLog, Media, QualityPoint, SiteMetric, SiteSetting, SocialLink, Value


@admin.register(SiteSetting)
class SiteSettingAdmin(AuditedModelAdmin):
    list_display = ("label", "key", "is_public", "updated_at")
    search_fields = ("key", "label", "value")
    list_filter = ("is_public",)


@admin.register(SocialLink)
class SocialLinkAdmin(AuditedModelAdmin):
    list_display = ("platform", "url", "is_active", "order")
    list_filter = ("platform", "is_active")
    ordering = ("order", "platform")


@admin.register(Media)
class MediaAdmin(AuditedModelAdmin):
    list_display = ("file", "alt_text", "created_at")
    search_fields = ("file", "alt_text", "description")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "object_repr", "user", "ip_address", "created_at")
    list_filter = ("action", "created_at")
    readonly_fields = [field.name for field in AuditLog._meta.fields]


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "page_path", "created_at")
    list_filter = ("event_type", "created_at")
    readonly_fields = [field.name for field in AnalyticsEvent._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(SiteMetric)
class SiteMetricAdmin(AuditedModelAdmin):
    list_display = ("value", "label", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("value", "label", "description")


@admin.register(Value)
class ValueAdmin(AuditedModelAdmin):
    list_display = ("name", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")


@admin.register(QualityPoint)
class QualityPointAdmin(AuditedModelAdmin):
    list_display = ("name", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")


@admin.register(AboutMilestone)
class AboutMilestoneAdmin(AuditedModelAdmin):
    list_display = ("year", "title", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("year", "title", "description")
