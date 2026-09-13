from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Achievements


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")


class AchievementsTest(TestCase):
    def test_achievements_url_and_template(self):
        response = self.client.get(reverse("main:show_achievements"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "achievements.html")

    def test_achievement_data_appears(self):
        Achievements.objects.create(
            title="Juara 1 Kompetisi Data Science",
            description="Meraih juara pertama dalam kompetisi data science.",
            field="Data Science",
            image_url="https://example.com/sertifikat.jpg",
        )

        response = self.client.get(reverse("main:show_achievements"))

        self.assertContains(response, "Juara 1 Kompetisi Data Science")
        self.assertContains(
            response,
            "Meraih juara pertama dalam kompetisi data science.",
        )
        self.assertContains(response, "Data Science")
        self.assertContains(
            response,
            'src="https://example.com/sertifikat.jpg"',
        )
        self.assertNotContains(
            response,
            "Belum ada prestasi yang ditambahkan.",
        )

    def test_empty_achievements_page(self):
        response = self.client.get(reverse("main:show_achievements"))

        self.assertContains(
            response,
            "Belum ada prestasi yang ditambahkan.",
        )