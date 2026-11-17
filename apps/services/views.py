from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, render
from django.db.models import Prefetch
from django.views.decorators.cache import never_cache

from apps.core.models import SiteMetric
from apps.faq.models import FAQItem

from .models import Expertise, Prestation


def expertise_list(request):
    return _catalog(request, "expertises")


def prestation_list(request):
    return _catalog(request, "prestations")


def _catalog(request, page_kind):
    active_prestations = Prefetch("prestations", queryset=Prestation.objects.filter(is_active=True))
    expertises = Expertise.objects.filter(is_active=True).prefetch_related(active_prestations)
    return render(request, "services/list.html", {
        "expertises": expertises,
        "expertise_count": expertises.count(),
        "page_kind": page_kind,
        "metrics": SiteMetric.objects.filter(is_active=True)[:3],
    })


def expertise_detail(request, slug):
    active_prestations = Prefetch("prestations", queryset=Prestation.objects.filter(is_active=True))
    related_expertises = Prefetch("related_expertises", queryset=Expertise.objects.filter(is_active=True))
    expertise = get_object_or_404(
        Expertise.objects.prefetch_related(active_prestations, related_expertises),
        slug=slug,
        is_active=True,
    )
    faqs = expertise.faq_categories.filter(is_active=True).prefetch_related(
        Prefetch("items", queryset=FAQItem.objects.filter(is_active=True))
    )
    return render(request, "services/detail.html", {"expertise": expertise, "faq_categories": faqs})


@never_cache
@staff_member_required(login_url="admin:login")
@permission_required("services.view_expertise", raise_exception=True)
def expertise_preview(request, pk):
    expertise = get_object_or_404(Expertise.objects.prefetch_related(
        "prestations", Prefetch("related_expertises", queryset=Expertise.objects.filter(is_active=True)),
    ), pk=pk)
    faqs = expertise.faq_categories.filter(is_active=True).prefetch_related(
        Prefetch("items", queryset=FAQItem.objects.filter(is_active=True))
    )
    return render(request, "services/detail.html", {"expertise": expertise, "faq_categories": faqs, "preview": True})
