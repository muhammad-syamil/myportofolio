from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from main.forms import AchievementForm
from main.models import Experience, Achievements


def show_main(request):
    context = {
        "name": "Muhammad Syamil",
        "npm": "2506547746",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Mahasiswa Ilmu Komputer Universitas Indonesia yang tertarik "
            "pada Data Science dan Artificial Intelligence."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Muhammad Syamil",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

def get_achievements_json(request):
    title_query = request.GET.get("title", "").strip()
    achievements = Achievements.objects.all()

    if title_query:
        achievements = achievements.filter(
            title__icontains=title_query
        )

    achievements_json = serializers.serialize("json", achievements)
    return HttpResponse(
        achievements_json,
        content_type="application/json",
    )


def show_achievements(request):
    json_response = get_achievements_json(request)

    achievements = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    achievements = [
        achievement.object for achievement in achievements
    ]
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Muhammad Syamil",
        "achievement_list": achievements,
        "title_query": title_query,
    }
    return render(request, "achievements.html", context)


def create_achievement(request):
    form = AchievementForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Prestasi baru berhasil ditambahkan!")
        return redirect("main:show_achievements")

    context = {
        "name": "Muhammad Syamil",
        "form": form,
    }
    return render(request, "achievement_form.html", context)


def delete_achievement(request, achievement_id):
    achievement = get_object_or_404(
        Achievements, pk=achievement_id
    )

    if request.method == "POST":
        achievement.delete()
        messages.success(request, "Prestasi berhasil dihapus!")
        return redirect("main:show_achievements")

    return redirect("main:show_achievements")