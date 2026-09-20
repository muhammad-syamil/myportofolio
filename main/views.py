from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from main.forms import AchievementForm, ExperienceForm
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
    response = get_experience_json(request)

    experience_list = [
        item.object
        for item in serializers.deserialize(
            "json",
            response.content.decode("utf-8"),
        )
    ]

    return render(request, "experience.html", {
        "name": "Muhammad Syamil",
        "experience_list": experience_list,
        "title_query": request.GET.get("title", "").strip(),
        "selected_category": request.GET.get("category", ""),
        "selected_status": request.GET.get("status", ""),
        "category_choices": Experience.EXPERIENCE_CHOICES,
        "has_filters": any(request.GET.get(key, "").strip() for key in ("title", "category", "status")),
    })

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

def get_experience_json(request):
    experiences = Experience.objects.all()
    title_query = request.GET.get("title", "").strip()
    category = request.GET.get("category", "")
    status = request.GET.get("status", "")

    if title_query:
        experiences = experiences.filter(title__icontains=title_query)
    if category:
        experiences = experiences.filter(category=category)
    if status in ("ongoing", "completed"):
        experiences = experiences.filter(ended_at__isnull=status == "ongoing")

    data = serializers.serialize("json", experiences)
    return HttpResponse(data, content_type="application/json")

def create_experience(request):
    form = ExperienceForm(
        request.POST if request.method == "POST" else None
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience berhasil ditambahkan!")
        return redirect("main:show_experience")

    return render(request, "experience_form.html", {
        "name": "Muhammad Syamil",
        "form": form,
        "page_title": "Tambah Experience",
    })

def update_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    form = ExperienceForm(
        request.POST if request.method == "POST" else None,
        instance=experience,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience berhasil diperbarui!")
        return redirect("main:show_experience")

    return render(request, "experience_form.html", {
        "name": "Muhammad Syamil",
        "form": form,
        "page_title": "Edit Experience",
    })

def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience berhasil dihapus!")

    return redirect("main:show_experience")
