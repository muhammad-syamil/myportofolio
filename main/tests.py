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
        self.assertContains(response, 'id="experience-loading"')
        self.assertContains(response, 'id="experience-error"')
        self.assertContains(response, 'id="experience-empty"')
        self.assertContains(response, 'id="experience-grid"')
        self.assertContains(response, "function escapeHtml")
        self.assertContains(response, "SEARCH_DEBOUNCE_DELAY = 300")
        self.assertContains(response, reverse("main:get_experience_json"))
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

        api_response = self.client.get(reverse("main:get_experience_json"))
        experience = api_response.json()[0]["fields"]
        self.assertEqual(experience["title"], self.experience.title)
        self.assertEqual(experience["description"], self.experience.description)
        self.assertEqual(experience["category_display"], "Part-Time")
        self.assertTrue(experience["is_ongoing"])

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))
        api_response = self.client.get(reverse("main:get_experience_json"))

        self.assertContains(
            response,
            "Belum ada pengalaman yang ditambahkan atau ditemukan.",
        )
        self.assertEqual(api_response.json(), [])

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:get_experience_json"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertFalse(response.json()[0]["fields"]["is_ongoing"])
        self.assertIsNotNone(response.json()[0]["fields"]["ended_at"])

    def test_navbar_updates_for_active_page_and_authenticated_user(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertContains(response, 'aria-current="page"')
        self.assertContains(response, reverse("main:register"))
        self.assertContains(response, reverse("main:login"))

        user = User.objects.create_user(username="navbar_user")
        self.client.force_login(user)
        response = self.client.get(reverse("main:show_main"))

        self.assertContains(response, user.username)
        self.assertContains(response, reverse("main:logout"))
        self.assertNotContains(response, reverse("main:register"))


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
        self.assertEqual(page.context["title_query"], "python")
        self.assertEqual(page.context["selected_category"], "volunteer")
        self.assertEqual(page.context["selected_status"], "ongoing")
        self.assertContains(page, 'value="volunteer" selected')
        self.assertContains(page, 'value="ongoing" selected')

    def test_completed_filter_and_empty_results(self):
        response = self.client.get(reverse("main:get_experience_json"), {"status": "completed"})
        self.assertEqual([item["fields"]["title"] for item in response.json()], ["Mentor Java"])
        empty_response = self.client.get(
            reverse("main:get_experience_json"),
            {"title": "Tidak cocok"},
        )
        self.assertEqual(empty_response.json(), [])

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
        response = self.client.post(delete_url, follow=True)
        self.assertContains(response, "Experience berhasil dihapus!")
        self.assertFalse(Experience.objects.filter(pk=experience.pk).exists())


class ExperienceJsonSecurityTest(TestCase):
    def test_json_exposes_only_required_fields_and_star_information(self):
        user = User.objects.create_user(username="api_user")
        experience = Experience.objects.create(
            title="Data Engineer",
            description="Mengolah data untuk kebutuhan analitik.",
            category="full-time",
        )
        experience.starred_by.add(user)

        response = self.client.get(reverse("main:get_experience_json"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(len(response.json()), 1)
        fields = response.json()[0]["fields"]
        self.assertSetEqual(
            set(fields),
            {
                "title",
                "description",
                "category",
                "category_display",
                "thumbnail",
                "started_at",
                "ended_at",
                "is_ongoing",
                "star_count",
                "is_starred",
                "starred_by_names",
            },
        )
        self.assertNotIn("starred_by", fields)
        self.assertEqual(fields["star_count"], 1)
        self.assertFalse(fields["is_starred"])
        self.assertEqual(fields["starred_by_names"], user.username)


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
        self.owner = User.objects.create_superuser(username="owner")

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

    def test_action_controls_follow_user_role(self):
        response = self.client.get(reverse("main:show_experience"))
        self.assertNotContains(response, self.create_url)
        self.assertContains(response, 'const IS_EDITOR = "false"')
        self.assertContains(response, 'const IS_SUPERUSER = "false"')

        self.client.force_login(self.regular_user)
        response = self.client.get(reverse("main:show_experience"))
        self.assertNotContains(response, self.create_url)
        self.assertContains(response, 'const IS_EDITOR = "false"')
        self.assertContains(response, 'const IS_SUPERUSER = "false"')

        self.client.force_login(self.editor)
        response = self.client.get(reverse("main:show_experience"))
        self.assertNotContains(response, self.create_url)
        self.assertContains(response, 'const IS_EDITOR = "true"')
        self.assertContains(response, 'const IS_SUPERUSER = "false"')

        self.client.force_login(self.owner)
        response = self.client.get(reverse("main:show_experience"))
        self.assertContains(response, self.create_url)
        self.assertContains(response, 'const IS_SUPERUSER = "true"')

    def test_json_displays_current_users_star_status_and_count(self):
        self.client.force_login(self.regular_user)
        self.client.post(self.star_url)

        response = self.client.get(reverse("main:get_experience_json"))
        fields = response.json()[0]["fields"]

        self.assertTrue(fields["is_starred"])
        self.assertEqual(fields["star_count"], 1)
        self.assertEqual(fields["starred_by_names"], self.regular_user.username)


class AchievementsTest(TestCase):
    def test_achievements_url_and_template(self):
        response = self.client.get(reverse("main:show_achievements"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "achievements.html")

    def test_achievement_data_appears_in_ajax_endpoint(self):
        achievement = Achievements.objects.create(
            title="Juara 1 Kompetisi Data Science",
            description="Meraih juara pertama dalam kompetisi data science.",
            field="Data Science",
            image_url="https://example.com/sertifikat.jpg",
        )

        response = self.client.get(reverse("main:get_achievements_json"))
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["pk"], str(achievement.pk))
        self.assertEqual(
            data[0]["fields"]["title"],
            "Juara 1 Kompetisi Data Science",
        )
        self.assertEqual(
            data[0]["fields"]["description"],
            "Meraih juara pertama dalam kompetisi data science.",
        )
        self.assertEqual(data[0]["fields"]["field"], "Data Science")
        self.assertEqual(
            data[0]["fields"]["image_url"],
            "https://example.com/sertifikat.jpg",
        )
        self.assertEqual(data[0]["fields"]["star_count"], 0)
        self.assertFalse(data[0]["fields"]["is_starred"])

    def test_achievements_page_contains_ajax_states(self):
        response = self.client.get(reverse("main:show_achievements"))

        self.assertContains(response, 'id="loading"')
        self.assertContains(response, 'id="error"')
        self.assertContains(response, 'id="empty"')
        self.assertContains(response, 'id="grid"')
        self.assertContains(response, reverse("main:get_achievements_json"))

    def test_achievement_search_is_applied_by_ajax_endpoint(self):
        Achievements.objects.create(
            title="Juara Data Science",
            description="Prestasi data.",
            field="Data Science",
        )
        Achievements.objects.create(
            title="Finalis Robotika",
            description="Prestasi robotika.",
            field="Robotika",
        )

        response = self.client.get(
            reverse("main:get_achievements_json"),
            {"title": "data"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(
            response.json()[0]["fields"]["title"],
            "Juara Data Science",
        )


class AchievementAuthorizationTest(TestCase):
    def setUp(self):
        self.achievement = Achievements.objects.create(
            title="Finalis Hackathon",
            description="Membangun aplikasi bersama tim.",
            field="Software Engineering",
        )
        self.regular_user = User.objects.create_user(username="achievement_user")
        self.editor = User.objects.create_user(username="achievement_editor")
        editor_group = Group.objects.create(name="Editor")
        self.editor.groups.add(editor_group)
        self.owner = User.objects.create_superuser(username="achievement_owner")

        self.list_url = reverse("main:show_achievements")
        self.update_url = reverse(
            "main:update_achievement",
            args=[self.achievement.pk],
        )

    def test_only_editor_and_owner_can_update_achievement(self):
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/login/?next="))

        self.client.force_login(self.regular_user)
        self.assertEqual(self.client.get(self.update_url).status_code, 403)

        self.client.force_login(self.editor)
        response = self.client.post(
            self.update_url,
            {
                "title": "Juara Hackathon",
                "description": self.achievement.description,
                "field": self.achievement.field,
                "image_url": "",
            },
            follow=True,
        )
        self.assertContains(response, "Prestasi berhasil diperbarui!")
        self.achievement.refresh_from_db()
        self.assertEqual(self.achievement.title, "Juara Hackathon")

        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(self.update_url).status_code, 200)
        self.assertContains(self.client.get(self.update_url), "Edit Prestasi")

    def test_edit_button_follows_achievement_role(self):
        response = self.client.get(self.list_url)
        self.assertContains(response, 'const IS_EDITOR = "false"')
        self.assertContains(response, 'const IS_SUPERUSER = "false"')

        self.client.force_login(self.regular_user)
        response = self.client.get(self.list_url)
        self.assertContains(response, 'const IS_EDITOR = "false"')
        self.assertContains(response, 'const IS_SUPERUSER = "false"')

        self.client.force_login(self.editor)
        response = self.client.get(self.list_url)
        self.assertContains(response, 'const IS_EDITOR = "true"')
        self.assertContains(response, 'const IS_SUPERUSER = "false"')

        self.client.force_login(self.owner)
        response = self.client.get(self.list_url)
        self.assertContains(response, 'const IS_SUPERUSER = "true"')
        self.assertContains(response, 'id="add-achievement-modal"')


class AchievementAjaxTest(TestCase):
    def setUp(self):
        self.regular_user = User.objects.create_user(username="ajax_user")
        self.owner = User.objects.create_superuser(username="ajax_owner")
        self.create_url = reverse("main:create_achievement_ajax")
        self.payload = {
            "title": "Juara Web Development",
            "description": "Membangun aplikasi Django.",
            "field": "Software Engineering",
            "image_url": "https://example.com/prestasi.jpg",
        }

    def test_ajax_create_only_accepts_post(self):
        self.client.force_login(self.owner)

        response = self.client.get(self.create_url)

        self.assertEqual(response.status_code, 405)

    def test_ajax_create_rejects_anonymous_and_regular_user(self):
        response = self.client.post(self.create_url, self.payload)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Achievements.objects.count(), 0)

        self.client.force_login(self.regular_user)
        response = self.client.post(self.create_url, self.payload)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Achievements.objects.count(), 0)

    def test_owner_can_create_achievement_with_ajax(self):
        self.client.force_login(self.owner)

        response = self.client.post(self.create_url, self.payload)

        self.assertEqual(response.status_code, 201)
        achievement = Achievements.objects.get()
        self.assertEqual(response.json()["pk"], str(achievement.pk))
        self.assertEqual(achievement.title, self.payload["title"])

    def test_ajax_create_returns_form_errors(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.create_url,
            {**self.payload, "title": "   "},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.json()["errors"])
        self.assertEqual(Achievements.objects.count(), 0)

    def test_form_strips_html_and_rejects_tag_only_title(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.create_url,
            {
                **self.payload,
                "title": "<b>Juara Web</b>",
                "description": "Belajar <em>Django</em>.",
                "field": "<strong>Web</strong>",
            },
        )

        self.assertEqual(response.status_code, 201)
        achievement = Achievements.objects.get()
        self.assertEqual(achievement.title, "Juara Web")
        self.assertEqual(achievement.description, "Belajar Django.")
        self.assertEqual(achievement.field, "Web")

        response = self.client.post(
            self.create_url,
            {
                **self.payload,
                "title": '<img src="x" onerror="alert(1)">',
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.json()["errors"])

    def test_json_includes_current_users_star_state(self):
        achievement = Achievements.objects.create(**self.payload)
        achievement.starred_by.add(self.regular_user)
        self.client.force_login(self.regular_user)

        response = self.client.get(reverse("main:get_achievements_json"))
        fields = response.json()[0]["fields"]

        self.assertEqual(fields["star_count"], 1)
        self.assertTrue(fields["is_starred"])
        self.assertEqual(fields["starred_by_names"], "ajax_user")
