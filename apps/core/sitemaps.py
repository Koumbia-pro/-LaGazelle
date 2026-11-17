from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.pages.models import Page
from apps.services.models import Expertise
from apps.stories.models import Article, CaseStudy


class StaticViewSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        items = ["pages:home", "pages:about", "expertises:list", "stories:advice", "faq:list", "contact:project"]
        published_legal_slugs = set(Page.objects.filter(
            slug__in=("mentions-legales", "politique-de-confidentialite"),
            status="published",
        ).values_list("slug", flat=True))
        if "mentions-legales" in published_legal_slugs:
            items.append("pages:legal-notice")
        if "politique-de-confidentialite" in published_legal_slugs:
            items.append("pages:privacy")
        if CaseStudy.objects.filter(status="published", client_authorized=True).exists():
            items.append("stories:cases")
        return items

    def location(self, item):
        return reverse(item)


class ExpertiseSitemap(Sitemap):
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return Expertise.objects.filter(is_active=True)


class PublishedPageSitemap(Sitemap):
    priority = 0.7
    changefreq = "monthly"

    def items(self):
        return Page.objects.filter(status="published").exclude(
            slug__in=("a-propos", "le-cabinet", "mentions-legales", "politique-de-confidentialite")
        )

    def location(self, item):
        return item.get_absolute_url()

    def lastmod(self, item):
        return item.updated_at


class ArticleSitemap(Sitemap):
    priority = 0.7
    changefreq = "monthly"

    def items(self):
        return Article.objects.filter(status="published", author__gt="", published_at__isnull=False)

    def lastmod(self, item):
        return item.updated_at


class CaseStudySitemap(Sitemap):
    priority = 0.6
    changefreq = "monthly"

    def items(self):
        return CaseStudy.objects.filter(status="published", client_authorized=True)

    def lastmod(self, item):
        return item.updated_at
