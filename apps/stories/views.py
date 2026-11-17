from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.db.models import Prefetch
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import never_cache
import json

from apps.faq.models import FAQCategory, FAQItem
from .models import Article, CaseStudy


def advice_list(request):
    categories = FAQCategory.objects.filter(is_active=True).prefetch_related(
        Prefetch("items", queryset=FAQItem.objects.filter(is_active=True))
    )
    categories = [category for category in categories if category.items.all()]
    items = [item for category in categories for item in category.items.all()]
    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{
            "@type": "Question",
            "name": item.question,
            "acceptedAnswer": {"@type": "Answer", "text": item.answer},
        } for item in items],
    }, ensure_ascii=False).replace("<", "\\u003C").replace(">", "\\u003E").replace("&", "\\u0026")
    return render(request, "stories/advice_list.html", {
        "articles": Article.objects.filter(status="published"),
        "categories": Article.CATEGORY_CHOICES,
        "faq_categories": categories,
        "featured_faq": items[0] if items else None,
        "faq_schema": schema,
    })


def article_detail(request, slug):
    article = get_object_or_404(Article.objects.prefetch_related("sections"), slug=slug, status="published")
    return render(request, "stories/article_detail.html", {"article": article})


def case_list(request):
    cases = CaseStudy.objects.filter(status="published", client_authorized=True)
    return render(request, "stories/case_list.html", {"cases": cases})


def case_detail(request, slug):
    case = get_object_or_404(CaseStudy, slug=slug, status="published", client_authorized=True)
    if case.client_name and not case.client_name_authorized:
        raise Http404
    return render(request, "stories/case_detail.html", {"case": case})


@never_cache
@staff_member_required(login_url="admin:login")
@permission_required("stories.view_article", raise_exception=True)
def article_preview(request, pk):
    article = get_object_or_404(Article.objects.prefetch_related("sections"), pk=pk)
    return render(request, "stories/article_detail.html", {"article": article, "preview": True})


@never_cache
@staff_member_required(login_url="admin:login")
@permission_required("stories.view_casestudy", raise_exception=True)
def case_preview(request, pk):
    case = get_object_or_404(CaseStudy, pk=pk)
    return render(request, "stories/case_detail.html", {"case": case, "preview": True})
