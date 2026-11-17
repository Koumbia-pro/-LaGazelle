from django.urls import path

from .views import expertise_detail, expertise_list, expertise_preview

app_name = "expertises"
urlpatterns = [
    path("", expertise_list, name="list"),
    path("apercu/<int:pk>/", expertise_preview, name="preview"),
    path("<slug:slug>/", expertise_detail, name="detail"),
]
