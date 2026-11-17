import json

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from django.views.decorators.cache import never_cache

from .models import FAQCategory, FAQItem


def faq_list(request):
    category_queryset = FAQCategory.objects.filter(is_active=True).select_related("expertise").prefetch_related(
        Prefetch("items", queryset=FAQItem.objects.filter(is_active=True))
    )
    categories = []
    faq_items = []
    for category in category_queryset:
        category.public_items = list(category.items.all())
        if category.public_items:
            categories.append(category)
            faq_items.extend(category.public_items)
    faq_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item.question,
                "acceptedAnswer": {"@type": "Answer", "text": item.answer},
            }
            for item in faq_items
        ],
    }, ensure_ascii=False).replace("<", "\\u003C").replace(">", "\\u003E").replace("&", "\\u0026")
    return render(request, "faq/list.html", {
        "categories": categories,
        "faq_schema": faq_schema,
        "category_count": len(categories),
        "faq_count": len(faq_items),
    })


@never_cache
@staff_member_required(login_url="admin:login")
@permission_required("faq.view_faqcategory", raise_exception=True)
def faq_preview(request, pk):
    category = get_object_or_404(FAQCategory.objects.prefetch_related("items"), pk=pk)
    category.public_items = list(category.items.all())
    items = category.public_items
    faq_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{
            "@type": "Question",
            "name": item.question,
            "acceptedAnswer": {"@type": "Answer", "text": item.answer},
        } for item in items],
    }, ensure_ascii=False).replace("<", "\\u003C").replace(">", "\\u003E").replace("&", "\\u0026")
    return render(request, "faq/list.html", {
        "categories": [category],
        "faq_schema": faq_schema,
        "category_count": 1,
        "faq_count": len(items),
        "preview": True,
    })
