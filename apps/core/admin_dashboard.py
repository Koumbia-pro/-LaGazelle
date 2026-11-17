from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from apps.contact.models import ProjectRequest
from apps.faq.models import FAQCategory, FAQItem
from apps.pages.models import Page
from apps.services.models import Expertise, Prestation
from apps.stories.models import Article, CaseStudy
from apps.team.models import TeamMember, TeamPole
from django.views.decorators.cache import never_cache

from .models import AboutMilestone, AuditLog, QualityPoint, SiteMetric, SiteSetting, SocialLink, Value


def _can_view(user, model):
    return user.is_superuser or user.has_perm(f"{model._meta.app_label}.view_{model._meta.model_name}")


def _can_add(user, model):
    return user.is_superuser or user.has_perm(f"{model._meta.app_label}.add_{model._meta.model_name}")


def _admin_url(model, suffix="changelist"):
    return reverse(f"admin:{model._meta.app_label}_{model._meta.model_name}_{suffix}")


@staff_member_required(login_url="admin:login")
@never_cache
def dashboard(request):
    content_definitions = [
        ("Éditorial", "Pages éditoriales", Page, "Pages publiques, textes institutionnels et SEO", "▤"),
        ("Éditorial", "Expertises", Expertise, "Les domaines de compétence de La Gazelle", "✦"),
        ("Éditorial", "Prestations", Prestation, "Les services associés aux expertises", "↗"),
        ("Éditorial", "Catégories FAQ", FAQCategory, "Organisation des questions fréquentes", "?"),
        ("Éditorial", "Questions FAQ", FAQItem, "Questions et réponses publiées", "≡"),
        ("Éditorial", "Conseils et articles", Article, "Articles, auteur, date et référencement", "✎"),
        ("Éditorial", "Réalisations documentées", CaseStudy, "Cas clients et autorisations de publication", "▧"),
        ("Équipe", "Pôles de l’équipe", TeamPole, "Organisation et expertises internes", "♙"),
        ("Équipe", "Membres de l’équipe", TeamMember, "Profils, rôles et présentations", "◉"),
        ("Identité du site", "Chiffres clés", SiteMetric, "Indicateurs affichés sur le site", "#"),
        ("Identité du site", "Valeurs", Value, "Les engagements de La Gazelle", "◇"),
        ("Identité du site", "Démarche qualité", QualityPoint, "Points de contrôle et de confiance", "✓"),
        ("Identité du site", "Jalons historiques", AboutMilestone, "Timeline de l’histoire de La Gazelle", "◷"),
        ("Identité du site", "Paramètres du site", SiteSetting, "Coordonnées et contenus transverses", "⚙"),
        ("Identité du site", "Réseaux sociaux", SocialLink, "Liens et comptes officiels", "◎"),
    ]

    content_cards = []
    content_groups = {}
    quick_actions = []
    for group, label, model, description, icon in content_definitions:
        if not _can_view(request.user, model):
            continue
        card = {
            "label": label,
            "description": description,
            "icon": icon,
            "count": model.objects.count(),
            "url": _admin_url(model),
        }
        content_cards.append(card)
        content_groups.setdefault(group, []).append(card)
        if _can_add(request.user, model):
            quick_actions.append({"label": f"Ajouter — {label}", "url": _admin_url(model, "add")})

    project_access = _can_view(request.user, ProjectRequest)
    project_stats = None
    recent_projects = []
    status_breakdown = []
    if project_access:
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        total_projects = ProjectRequest.objects.count()
        project_stats = {
            "total": total_projects,
            "new": ProjectRequest.objects.filter(status="new").count(),
            "in_progress": ProjectRequest.objects.filter(status="in_progress").count(),
            "treated": ProjectRequest.objects.filter(status="treated").count(),
            "this_month": ProjectRequest.objects.filter(created_at__gte=month_start).count(),
        }
        recent_projects = ProjectRequest.objects.all()[:6]
        counts = {
            row["status"]: row["total"]
            for row in ProjectRequest.objects.values("status").annotate(total=Count("id"))
        }
        status_breakdown = []
        for key, label in ProjectRequest.STATUS_CHOICES:
            count = counts.get(key, 0)
            status_breakdown.append({
                "key": key,
                "label": label,
                "count": count,
                "percent": round((count / total_projects) * 100) if total_projects else 0,
            })
        if _can_add(request.user, ProjectRequest):
            quick_actions.insert(0, {"label": "Ajouter — demande de projet", "url": _admin_url(ProjectRequest, "add")})

    audit_access = _can_view(request.user, AuditLog)
    recent_activity = AuditLog.objects.select_related("user").all()[:8] if audit_access else []
    if request.user.is_superuser:
        role_label = "Super administrateur"
    else:
        role_label = request.user.groups.order_by("name").values_list("name", flat=True).first() or "Équipe d’administration"

    return render(request, "admin/dashboard.html", {
        "content_cards": content_cards,
        "content_groups": [{"label": label, "cards": cards} for label, cards in content_groups.items()],
        "quick_actions": quick_actions[:8],
        "project_access": project_access,
        "project_stats": project_stats,
        "recent_projects": recent_projects,
        "status_breakdown": status_breakdown,
        "audit_access": audit_access,
        "recent_activity": recent_activity,
        "role_label": role_label,
        "dashboard_updated_at": timezone.localtime(),
        "public_site_url": reverse("pages:home"),
    })
