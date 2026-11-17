from django.urls import path

from .views import faq_list, faq_preview

app_name = "faq"
urlpatterns = [
    path("apercu/<int:pk>/", faq_preview, name="preview"),
    path("", faq_list, name="list"),
]
