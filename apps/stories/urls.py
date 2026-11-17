from django.urls import path

from .views import advice_list, article_detail, article_preview, case_detail, case_list, case_preview

app_name = "stories"
urlpatterns = [
    path("conseils/", advice_list, name="advice"),
    path("conseils/apercu/<int:pk>/", article_preview, name="article-preview"),
    path("conseils/<slug:slug>/", article_detail, name="article"),
    path("realisations/", case_list, name="cases"),
    path("realisations/apercu/<int:pk>/", case_preview, name="case-preview"),
    path("realisations/<slug:slug>/", case_detail, name="case"),
]
