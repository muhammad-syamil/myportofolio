from django.urls import path

from main.views import (
    show_main,
    show_experience,
    show_achievements,
    create_achievement,
    get_achievements_json,
    delete_achievement,
    create_experience,
    update_experience,
    delete_experience,
    toggle_experience_star,
    get_experience_json,
    login_user,
    logout_user,
    register,
    toggle_star,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("experience/", show_experience, name="show_experience"),
    path("achievements/", show_achievements, name="show_achievements"),
    path(
        "achievements/add/",
        create_achievement,
        name="create_achievement",
    ),
    path(
        "api/achievements/",
        get_achievements_json,
        name="get_achievements_json",
    ),
    path(
        "achievements/<int:achievement_id>/delete/",
        delete_achievement,
        name="delete_achievement",
    ),
    path(
        "achievements/<int:achievement_id>/star/",
        toggle_star,
        name="toggle_star",
    ),

    path(
    "experience/add/",
    create_experience,
    name="create_experience",
    ),
    path(
        "experience/<uuid:experience_id>/edit/",
        update_experience,
        name="update_experience",
    ),
    path(
        "experience/<uuid:experience_id>/delete/",
        delete_experience,
        name="delete_experience",
    ),
    path(
        "experience/<uuid:experience_id>/star/",
        toggle_experience_star,
        name="toggle_experience_star",
    ),
    path(
        "api/experience/",
        get_experience_json,
        name="get_experience_json",
    ),
]
