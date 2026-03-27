from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Author, Category, Post, ResourceGroup, ResourceLink, ResourceSection

User = get_user_model()
TEST_GIF_BYTES = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00"
    b"\xff\xff\xff!\xf9\x04\x00\x00\x00\x00\x00,\x00"
    b"\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


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

    def test_resource_library_page_renders_uploaded_file(self):
        section = ResourceSection.objects.create(
            title="File section",
            slug="file-section",
            display_order=10,
        )
        group = ResourceGroup.objects.create(
            section=section,
            title="Files",
            display_order=1,
        )
        ResourceLink.objects.create(
            group=group,
            title="Grammar PDF",
            document=SimpleUploadedFile("grammar.pdf", b"pdf-content"),
            display_order=1,
        )

        response = self.client.get(reverse("resource_library"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Grammar PDF")
        self.assertContains(response, "grammar")


class ResourceAdminTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="staffuser",
            password="strong-password-123",
            is_staff=True,
        )
        self.author = Author.objects.create(
            user=self.user,
            profile_picture=SimpleUploadedFile("avatar.gif", TEST_GIF_BYTES, content_type="image/gif"),
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

    def test_database_page_filters_by_query(self):
        self.client.login(username="staffuser", password="strong-password-123")
        section = ResourceSection.objects.create(title="Japanese", slug="japanese")
        group = ResourceGroup.objects.create(section=section, title="N5")
        ResourceLink.objects.create(group=group, title="Listening", url="https://example.com/listening")
        ResourceLink.objects.create(group=group, title="Kanji", url="https://example.com/kanji")

        response = self.client.get(reverse("resource_admin_database"), {"q": "Listening"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Listening")
        self.assertNotContains(response, "https://example.com/kanji")

    def test_staff_can_access_category_create_page(self):
        self.client.login(username="staffuser", password="strong-password-123")

        response = self.client.get(reverse("category_create"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create category")

    def test_staff_can_access_post_create_page(self):
        self.client.login(username="staffuser", password="strong-password-123")
        Category.objects.create(
            title="Learn",
            subtitle="Study notes",
            slug="learn",
            thumbnail=SimpleUploadedFile("learn.jpg", b"image-bytes", content_type="image/jpeg"),
        )

        response = self.client.get(reverse("post_create"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create post")

    def test_post_create_page_uses_author_name_input(self):
        self.client.login(username="staffuser", password="strong-password-123")
        Category.objects.create(
            title="Learn",
            subtitle="Study notes",
            slug="learn",
            thumbnail=SimpleUploadedFile("learn.jpg", b"image-bytes", content_type="image/jpeg"),
        )

        response = self.client.get(reverse("post_create"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="author_name"')

    def test_staff_can_create_post_with_typed_author_name(self):
        self.client.login(username="staffuser", password="strong-password-123")
        category = Category.objects.create(
            title="Learn",
            subtitle="Study notes",
            slug="learn",
            thumbnail=SimpleUploadedFile("learn.jpg", b"image-bytes", content_type="image/jpeg"),
        )

        response = self.client.post(
            reverse("post_create"),
            {
                "title": "Hoc ngu phap",
                "slug": "hoc-ngu-phap",
                "overview": "Tong hop ngu phap can ban",
                "content": "Noi dung bai viet",
                "author_name": "Sensei Hana",
                "categories": [category.id],
                "featured": "on",
                "thumbnail": SimpleUploadedFile("post.gif", TEST_GIF_BYTES, content_type="image/gif"),
            },
        )

        self.assertEqual(response.status_code, 302)
        post = Post.objects.get(slug="hoc-ngu-phap")
        self.assertEqual(str(post.author), "Sensei Hana")
        self.assertEqual(post.author.display_name, "Sensei Hana")

    def test_database_page_post_table_has_edit_delete_actions(self):
        self.client.login(username="staffuser", password="strong-password-123")
        category = Category.objects.create(
            title="Computer",
            subtitle="Tech",
            slug="computer",
            thumbnail=SimpleUploadedFile("computer.jpg", b"image-bytes", content_type="image/jpeg"),
        )
        post = Post.objects.create(
            title="May tinh co ban",
            slug="may-tinh-co-ban",
            overview="Gioi thieu tong quan",
            content="Noi dung",
            author=self.author,
            thumbnail=SimpleUploadedFile("thumb.gif", TEST_GIF_BYTES, content_type="image/gif"),
            featured=False,
        )
        post.categories.add(category)

        response = self.client.get(reverse("resource_admin_database"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("post_update", args=[post.id]))
        self.assertContains(response, reverse("post_delete", args=[post.id]))
