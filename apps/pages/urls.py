from django.urls import path
from django.views.generic import RedirectView

from .views import about, home, legal_page, page_detail, page_preview

app_name = "pages"
urlpatterns = [
    path("", home, name="home"),
    path("le-cabinet/", about, name="about"),
    path("a-propos/", RedirectView.as_view(pattern_name="pages:about", permanent=True)),
    path("mentions-legales/", lambda request: legal_page(request, "mentions-legales"), name="legal-notice"),
    path("confidentialite/", lambda request: legal_page(request, "politique-de-confidentialite"), name="privacy"),
    path("politique-de-confidentialite/", RedirectView.as_view(pattern_name="pages:privacy", permanent=True)),
    path("apercu/page/<int:pk>/", page_preview, name="page-preview"),
    path("pages/<slug:slug>/", page_detail, name="page"),
]
