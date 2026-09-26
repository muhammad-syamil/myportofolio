from django.contrib.auth.models import Group, User
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


class ExperienceFeaturesTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="portfolio_owner",
            password="test-password",
        )
        self.client.force_login(self.owner)
        self.active = Experience.objects.create(
            title="Mentor Python", description="Mengajar", category="volunteer"
        )
        Experience.objects.create(
            title="Mentor Java", description="Mengajar", category="volunteer",
            ended_at=timezone.now(),
        )
        Experience.objects.create(
            title="Mentor Python Internship", description="Magang", category="internship"
        )

    def test_combined_filters_match_json_and_page(self):
        filters = {"title": " python ", "category": "volunteer", "status": "ongoing"}
        response = self.client.get(reverse("main:get_experience_json"), filters)
        self.assertEqual([item["pk"] for item in response.json()], [str(self.active.pk)])
        page = self.client.get(reverse("main:show_experience"), filters)
        self.assertEqual([item.pk for item in page.context["experience_list"]], [self.active.pk])
        self.assertContains(page, 'value="volunteer" selected')
        self.assertContains(page, 'value="ongoing" selected')

    def test_completed_filter_and_empty_results(self):
        response = self.client.get(reverse("main:get_experience_json"), {"status": "completed"})
        self.assertEqual([item["fields"]["title"] for item in response.json()], ["Mentor Java"])
        page = self.client.get(reverse("main:show_experience"), {"title": "Tidak cocok"})
        self.assertContains(page, "Tidak ada pengalaman yang sesuai")

    def test_create_update_and_delete_messages(self):
        data = {"title": "Pengalaman baru", "description": "Deskripsi", "category": "research", "thumbnail": ""}
        response = self.client.post(reverse("main:create_experience"), data, follow=True)
        self.assertContains(response, "Experience berhasil ditambahkan!")
        experience = Experience.objects.get(title=data["title"])
        count = Experience.objects.count()
        data["title"] = "Pengalaman diperbarui"
        response = self.client.post(reverse("main:update_experience", args=[experience.pk]), data, follow=True)
        self.assertContains(response, "Experience berhasil diperbarui!")
        self.assertEqual(Experience.objects.count(), count)
        experience.refresh_from_db()
        self.assertEqual(experience.title, data["title"])
        delete_url = reverse("main:delete_experience", args=[experience.pk])
        self.client.get(delete_url)
        self.assertTrue(Experience.objects.filter(pk=experience.pk).exists())
        self.assertContains(response, f'popovertarget="delete-experience-{experience.pk}"')
        response = self.client.post(delete_url, follow=True)
        self.assertContains(response, "Experience berhasil dihapus!")
        self.assertFalse(Experience.objects.filter(pk=experience.pk).exists())


class ExperienceAuthorizationTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Backend Developer",
            description="Membangun layanan web.",
            category="internship",
        )
        self.regular_user = User.objects.create_user(username="regular")
        self.editor = User.objects.create_user(username="editor")
        editor_group = Group.objects.create(name="Editor")
        self.editor.groups.add(editor_group)

        self.create_url = reverse("main:create_experience")
        self.update_url = reverse(
            "main:update_experience",
            args=[self.experience.pk],
        )
        self.delete_url = reverse(
            "main:delete_experience",
            args=[self.experience.pk],
        )
        self.star_url = reverse(
            "main:toggle_experience_star",
            args=[self.experience.pk],
        )

    def test_anonymous_actions_redirect_to_login(self):
        protected_requests = (
            self.client.get(self.create_url),
            self.client.get(self.update_url),
            self.client.post(self.delete_url),
            self.client.post(self.star_url),
        )

        for response in protected_requests:
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith("/login/?next="))

    def test_regular_user_can_only_toggle_star(self):
        self.client.force_login(self.regular_user)

        self.assertEqual(self.client.get(self.create_url).status_code, 403)
        self.assertEqual(self.client.get(self.update_url).status_code, 403)
        self.assertEqual(self.client.post(self.delete_url).status_code, 403)
        self.assertEqual(self.client.get(self.star_url).status_code, 405)

        self.client.post(self.star_url)
        self.assertTrue(
            self.experience.starred_by.filter(pk=self.regular_user.pk).exists()
        )

        self.client.post(self.star_url)
        self.assertFalse(
            self.experience.starred_by.filter(pk=self.regular_user.pk).exists()
        )

    def test_editor_can_update_but_cannot_create_or_delete(self):
        self.client.force_login(self.editor)
        updated_data = {
            "title": "Senior Backend Developer",
            "description": self.experience.description,
            "category": self.experience.category,
            "thumbnail": "",
        }

        self.assertEqual(self.client.get(self.create_url).status_code, 403)
        response = self.client.post(self.update_url, updated_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.post(self.delete_url).status_code, 403)

        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, updated_data["title"])


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
