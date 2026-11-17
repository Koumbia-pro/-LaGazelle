from django.urls import path

from .views import expertise_detail, expertise_list

app_name = "services"
urlpatterns = [
    path("", expertise_list, name="list"),
    path("<slug:slug>/", expertise_detail, name="detail"),
]
