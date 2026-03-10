from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import ResourceGroup, ResourceLink, ResourceSection

User = get_user_model()


class ResourceLibraryViewTests(TestCase):
    def test_resource_library_page_renders_sections(self):
        section = ResourceSection.objects.create(
            title="Thu vien test",
            slug="thu-vien-test",
            display_order=1,
        )
        group = ResourceGroup.objects.create(
            section=section,
            title="N5",
            display_order=1,
        )
        ResourceLink.objects.create(
            group=group,
            title="File nghe",
            url="https://example.com/audio",
            display_order=1,
        )

        response = self.client.get(reverse("resource_library"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Thu vien test")
        self.assertContains(response, "File nghe")


class ResourceAdminTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="staffuser",
            password="strong-password-123",
            is_staff=True,
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("resource_admin_dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("resource_admin_login"), response.url)

    def test_staff_can_login_and_access_dashboard(self):
        logged_in = self.client.login(username="staffuser", password="strong-password-123")
        self.assertTrue(logged_in)

        response = self.client.get(reverse("resource_admin_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard")

    def test_staff_can_access_database_page(self):
        self.client.login(username="staffuser", password="strong-password-123")

        response = self.client.get(reverse("resource_admin_database"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Database viewer")
