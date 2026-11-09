from django.urls import path

from main import api_views

app_name = "api"

urlpatterns = [
    path("experience/", api_views.experience_list, name="experience-list"),
    path("experience/<uuid:experience_id>/", api_views.experience_detail, name="experience-detail"),
    path("experience/<uuid:experience_id>/star/", api_views.experience_star, name="experience-star"),
    path("achievements/", api_views.achievement_list, name="achievement-list"),
    path("achievements/<int:achievement_id>/", api_views.achievement_detail, name="achievement-detail"),
    path("achievements/<int:achievement_id>/star/", api_views.achievement_star, name="achievement-star"),
]
