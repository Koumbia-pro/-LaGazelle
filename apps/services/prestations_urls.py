from django.urls import path
from django.views.generic import RedirectView

app_name = "prestations"
urlpatterns = [path("", RedirectView.as_view(pattern_name="expertises:list", permanent=True), name="list")]
