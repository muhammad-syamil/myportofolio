from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Achievements


class AchievementAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="achievement_owner", password="test-password"
        )
        self.editor = User.objects.create_user(
            username="achievement_editor", password="test-password"
        )
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.regular = User.objects.create_user(
            username="achievement_regular", password="test-password"
        )
        self.achievement = Achievements.objects.create(
            title="Juara Robotika", description="Membuat robot.", field="Robotika"
        )
        self.list_url = reverse("api:achievement-list")
        self.detail_url = reverse("api:achievement-detail", args=[self.achievement.pk])
        self.star_url = reverse("api:achievement-star", args=[self.achievement.pk])
        self.payload = {
            "title": "Finalis Hackathon",
            "description": "Membangun aplikasi.",
            "field": "Software Engineering",
            "image_url": "https://example.com/prestasi.jpg",
        }

    def test_public_list_detail_search_and_empty_results(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], self.achievement.pk)
        self.assertEqual(response.data[0]["star_count"], 0)
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])
        self.assertNotIn("email", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(self.client.get(self.list_url, {"title": "  ROBOT  "}).data), 1
        )
        self.assertEqual(self.client.get(self.list_url, {"title": "tidak ada"}).data, [])

    def test_missing_detail_returns_404(self):
        url = reverse("api:achievement-detail", args=[self.achievement.pk + 999])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_regular_cannot_manage_and_data_does_not_change(self):
        for user in (None, self.regular):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(
                self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code,
                403,
            )
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Achievements.objects.count(), 1)
        self.achievement.refresh_from_db()
        self.assertEqual(self.achievement.title, "Juara Robotika")

    def test_editor_can_patch_and_put_but_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        response = self.client.patch(self.detail_url, {"title": "Juara Web"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.achievement.refresh_from_db()
        self.assertEqual(self.achievement.title, "Juara Web")
        self.assertEqual(self.achievement.description, "Membuat robot.")
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.achievement.refresh_from_db()
        self.assertEqual(self.achievement.title, self.payload["title"])
        self.assertEqual(Achievements.objects.count(), 1)

    def test_owner_can_create_update_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_id = response.data["id"]
        self.assertTrue(Achievements.objects.filter(pk=created_id).exists())
        self.assertEqual(
            self.client.patch(self.detail_url, {"field": "Teknologi"}, format="json").status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(self.client.delete(self.detail_url).status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Achievements.objects.filter(pk=self.achievement.pk).exists())

    def test_validation_and_text_cleaning(self):
        self.client.force_authenticate(user=self.owner)
        for change, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"field": "<b></b>"}, "field"),
            ({"image_url": "javascript:alert(1)"}, "image_url"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **change}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        self.assertEqual(Achievements.objects.count(), 1)
        response = self.client.post(
            self.list_url,
            {**self.payload, "title": "<b>Finalis</b>", "field": "<em>Web</em>"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Finalis")
        self.assertEqual(response.data["field"], "Web")

    def test_put_requires_all_required_fields(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.put(self.detail_url, {"title": "Incomplete"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.achievement.refresh_from_db()
        self.assertEqual(self.achievement.title, "Juara Robotika")

    def test_star_requires_login_and_uses_current_user(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.achievement.starred_by.count(), 0)
        self.client.force_authenticate(user=self.regular)
        response = self.client.post(self.star_url, {"user_id": self.owner.pk}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertEqual(response.data["starred_by_names"], self.regular.username)
        self.assertFalse(self.achievement.starred_by.filter(pk=self.owner.pk).exists())
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_computed_fields_cannot_be_written(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url,
            {**self.payload, "star_count": 99, "is_starred": True,
             "starred_by_names": "forged", "starred_by": [self.regular.pk]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])

    def test_wrong_methods(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.get(self.star_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="achievement_owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Achievements.objects.count(), 1)

    def test_session_write_with_page_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="achievement_owner", password="test-password"))
        page = client.get(reverse("main:show_achievements"))
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_regular_user_can_star_with_page_csrf(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="achievement_regular", password="test-password"))
        page = client.get(reverse("main:show_achievements"))
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(self.star_url, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_starred"])
