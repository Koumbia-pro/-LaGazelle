from django.contrib import admin

from apps.core.admin_mixins import AuditedModelAdmin

from .models import TeamMember, TeamPole


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 1


@admin.register(TeamPole)
class TeamPoleAdmin(AuditedModelAdmin):
    list_display = ("name", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    inlines = [TeamMemberInline]


@admin.register(TeamMember)
class TeamMemberAdmin(AuditedModelAdmin):
    list_display = ("name", "role", "pole", "is_active", "is_verified")
    list_filter = ("is_active", "is_verified", "pole")
    search_fields = ("name", "role", "bio")
