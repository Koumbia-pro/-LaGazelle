import re

from django.conf import settings

from apps.pages.models import Page

from .models import SiteSetting, SocialLink


def site_context(request):
    site_settings = {item.key: item.value for item in SiteSetting.objects.filter(is_public=True)}
    published_legal_slugs = set(Page.objects.filter(
        status="published",
        slug__in=("mentions-legales", "politique-de-confidentialite"),
    ).values_list("slug", flat=True))
    phone = site_settings.get("site_phone_standard", "")
    whatsapp = site_settings.get("site_whatsapp", "")
    return {
        "site_settings": site_settings,
        "social_links": SocialLink.objects.filter(is_active=True, url__gt=""),
        "hcaptcha_site_key": settings.HCAPTCHA_SITE_KEY,
        "search_indexing_enabled": settings.SEARCH_INDEXING_ENABLED,
        "canonical_url": request.build_absolute_uri(request.path),
        "legal_notice_available": "mentions-legales" in published_legal_slugs,
        "privacy_page_available": "politique-de-confidentialite" in published_legal_slugs,
        "phone_uri": re.sub(r"[^0-9+]", "", phone),
        "whatsapp_uri": re.sub(r"\D", "", whatsapp),
    }
