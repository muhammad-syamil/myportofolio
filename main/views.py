import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from main.forms import AchievementForm, ExperienceForm
from main.models import Experience, Achievements


def _is_editor(user):
    return user.groups.filter(name="Editor").exists()


def show_main(request):
    last_login = request.COOKIES.get(
        "last_login",
        "Belum ada sesi login / Cookie tidak ditemukan",
    )
    context = {
        "name": "Muhammad Syamil",
        "npm": "2506547746",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Mahasiswa Ilmu Komputer Universitas Indonesia yang tertarik "
            "pada Data Science dan Artificial Intelligence."
        ),
        "last_login": last_login,
    }
    return render(request, "index.html", context)


def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Muhammad Syamil",
        "form": form,
    }
    return render(request, "register.html", context)


def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie(
            "last_login",
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        return response

    context = {
        "name": "Muhammad Syamil",
        "form": form,
    }
    return render(request, "login.html", context)


def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login")
    return response


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

    achievements_json = serializers.serialize(
        "json",
        achievements,
        use_natural_foreign_keys=True,
    )
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


@login_required(login_url="/login/")
def create_achievement(request):
    if not request.user.is_superuser:
        raise PermissionDenied

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


@login_required(login_url="/login/")
def delete_achievement(request, achievement_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    achievement = get_object_or_404(
        Achievements, pk=achievement_id
    )

    if request.method == "POST":
        achievement.delete()
        messages.success(request, "Prestasi berhasil dihapus!")
        return redirect("main:show_achievements")

    return redirect("main:show_achievements")


@login_required(login_url="/login/")
def toggle_star(request, achievement_id):
    achievement = get_object_or_404(
        Achievements,
        pk=achievement_id,
    )

    if request.method == "POST":
        if request.user in achievement.starred_by.all():
            achievement.starred_by.remove(request.user)
        else:
            achievement.starred_by.add(request.user)

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

@login_required(login_url="/login/")
def create_experience(request):
    if not request.user.is_superuser:
        raise PermissionDenied

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

@login_required(login_url="/login/")
def update_experience(request, experience_id):
    if not (request.user.is_superuser or _is_editor(request.user)):
        raise PermissionDenied

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

@login_required(login_url="/login/")
def delete_experience(request, experience_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience berhasil dihapus!")

    return redirect("main:show_experience")


@login_required(login_url="/login/")
@require_POST
def toggle_experience_star(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.user in experience.starred_by.all():
        experience.starred_by.remove(request.user)
    else:
        experience.starred_by.add(request.user)

    return redirect("main:show_experience")
