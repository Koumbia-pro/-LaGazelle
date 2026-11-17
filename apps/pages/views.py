from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.views.decorators.cache import never_cache
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from apps.faq.models import FAQItem
from apps.services.models import Expertise
from apps.stories.models import CaseStudy

from .models import Page


def home(request):
    context = {
        "expertises": Expertise.objects.filter(is_active=True),
        "faq_items": FAQItem.objects.filter(is_active=True, category__is_active=True).select_related("category")[:5],
        "cases": CaseStudy.objects.filter(status="published", client_authorized=True)[:3],
    }
    return render(request, "pages/home.html", context)


def about(request):
    page = Page.objects.filter(slug="le-cabinet", status="published").first()
    return render(request, "pages/about.html", {
        "page": page,
        "expertises": Expertise.objects.filter(is_active=True),
    })


def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug, status="published")
    return render(request, "pages/page_detail.html", {"page": page})


@never_cache
@staff_member_required(login_url="admin:login")
@permission_required("pages.view_page", raise_exception=True)
def page_preview(request, pk):
    page = get_object_or_404(Page, pk=pk)
    return render(request, "pages/page_detail.html", {"page": page, "preview": True})


def legal_page(request, kind):
    pending_pages = {
        "mentions-legales": (
            "Mentions légales",
            "Les informations légales de La Gazelle sont en cours de vérification.",
            "Les informations concernant l’éditeur, le responsable de publication et l’hébergeur seront publiées après validation.",
        ),
        "politique-de-confidentialite": (
            "Confidentialité",
            "La politique de confidentialité est en cours de finalisation.",
            "Les détails sur les données traitées, leur durée de conservation et les prestataires seront publiés après vérification. Le formulaire de contact reste indisponible tant que cette politique n’est pas finalisée.",
        ),
    }
    if kind not in pending_pages:
        raise Http404("Cette page n’existe pas.")

    editable_page = Page.objects.filter(slug=kind, status="published").first()
    if editable_page:
        return render(request, "pages/legal.html", {
            "title": editable_page.title,
            "intro": editable_page.intro,
            "content": editable_page.content,
            "page": editable_page,
            "legal_page_pending": False,
        })

    title, intro, pending_message = pending_pages[kind]
    return render(request, "pages/legal.html", {
        "title": title,
        "intro": intro,
        "pending_message": pending_message,
        "legal_page_pending": True,
    })
