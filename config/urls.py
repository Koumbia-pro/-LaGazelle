from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView

from apps.core.sitemaps import ArticleSitemap, CaseStudySitemap, ExpertiseSitemap, PublishedPageSitemap, StaticViewSitemap
from apps.core.admin_dashboard import dashboard
from apps.core.views import record_conversion

admin.site.site_header = "La Gazelle — Administration"
admin.site.site_title = "La Gazelle"
admin.site.index_title = "Espace de gestion"

sitemaps = {
    "static": StaticViewSitemap,
    "expertises": ExpertiseSitemap,
    "content_pages": PublishedPageSitemap,
    "articles": ArticleSitemap,
    "cases": CaseStudySitemap,
}

urlpatterns = [
    path("admin/", dashboard, name="admin-dashboard"),
    path("admin/", admin.site.urls),
    path("", include("apps.pages.urls")),
    path("expertises/", include("apps.services.expertises_urls")),
    path("prestations/", include("apps.services.prestations_urls")),
    path("faq/", include("apps.faq.urls")),
    path("contact/", include("apps.contact.urls")),
    path("projet/", RedirectView.as_view(pattern_name="contact:project", permanent=True)),
    path("services/", RedirectView.as_view(pattern_name="expertises:list", permanent=True)),
    path("equipe/", include("apps.team.urls")),
    path("", include("apps.stories.urls")),
    path("mesure/conversion/", record_conversion, name="conversion-event"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain"), name="robots"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
