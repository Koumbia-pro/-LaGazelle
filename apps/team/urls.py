from django.urls import path

from .views import team_list

app_name = "team"
urlpatterns = [path("", team_list, name="list")]
