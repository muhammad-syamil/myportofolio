from django.shortcuts import render

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

def show_achievements(request):
    context = {
        "achievement_list": Achievements.objects.all(),
    }
    return render(request, "achievements.html", context)