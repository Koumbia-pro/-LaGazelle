from django.urls import path

from .views import project_attachment, project_request

app_name = "contact"
urlpatterns = [
    path("", project_request, name="project"),
    path("<int:pk>/piece-jointe/", project_attachment, name="attachment"),
]
