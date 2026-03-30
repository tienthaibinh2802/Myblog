from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages

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
                "status": Post.STATUS_PUBLISHED,
                "featured": "on",
                "thumbnail": SimpleUploadedFile("post.gif", TEST_GIF_BYTES, content_type="image/gif"),
            },
        )

        self.assertEqual(response.status_code, 302)
        post = Post.objects.get(slug="hoc-ngu-phap")
        self.assertEqual(str(post.author), "Sensei Hana")
        self.assertEqual(post.author.display_name, "Sensei Hana")
        self.assertEqual(post.status, Post.STATUS_PUBLISHED)

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
        self.assertContains(response, reverse("post", args=[post.slug]))
        self.assertContains(response, "Published")
        self.assertContains(response, reverse("post_duplicate", args=[post.id]))
        self.assertContains(response, reverse("post_update", args=[post.id]))
        self.assertContains(response, reverse("post_delete", args=[post.id]))
        self.assertContains(response, "Categories")

    def test_database_page_can_filter_posts_by_category_and_author_name(self):
        self.client.login(username="staffuser", password="strong-password-123")
        learn_category = Category.objects.create(
            title="Learn Nihongo",
            subtitle="Study",
            slug="learn-nihongo",
            thumbnail=SimpleUploadedFile("learn-category.gif", TEST_GIF_BYTES, content_type="image/gif"),
        )
        review_category = Category.objects.create(
            title="Reviews",
            subtitle="Review",
            slug="reviews",
            thumbnail=SimpleUploadedFile("review-category.gif", TEST_GIF_BYTES, content_type="image/gif"),
        )
        typed_author = Author.objects.create(
            user=User.objects.create_user(username="sensei-hana"),
            display_name="Sensei Hana",
        )
        matching_post = Post.objects.create(
            title="Ngu phap N5",
            slug="ngu-phap-n5",
            overview="Tong hop ngu phap",
            content="Hoc voi Sensei Hana",
            author=typed_author,
            thumbnail=SimpleUploadedFile("post-1.gif", TEST_GIF_BYTES, content_type="image/gif"),
            featured=True,
        )
        matching_post.categories.add(learn_category)
        other_post = Post.objects.create(
            title="May tinh",
            slug="may-tinh",
            overview="Review laptop",
            content="Noi dung review",
            author=self.author,
            thumbnail=SimpleUploadedFile("post-2.gif", TEST_GIF_BYTES, content_type="image/gif"),
            featured=False,
        )
        other_post.categories.add(review_category)

        response = self.client.get(
            reverse("resource_admin_database"),
            {"q": "Sensei Hana", "category": learn_category.id, "featured": "yes"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ngu phap N5")
        self.assertNotContains(response, "May tinh")

    def test_database_page_can_filter_posts_by_status(self):
        self.client.login(username="staffuser", password="strong-password-123")
        published_post = Post.objects.create(
            title="Published post",
            slug="published-post",
            overview="Mo ta",
            content="Noi dung",
            author=self.author,
            thumbnail=SimpleUploadedFile("published.gif", TEST_GIF_BYTES, content_type="image/gif"),
            featured=False,
            status=Post.STATUS_PUBLISHED,
        )
        draft_post = Post.objects.create(
            title="Draft post",
            slug="draft-post",
            overview="Mo ta",
            content="Noi dung",
            author=self.author,
            thumbnail=SimpleUploadedFile("draft.gif", TEST_GIF_BYTES, content_type="image/gif"),
            featured=False,
            status=Post.STATUS_DRAFT,
        )

        response = self.client.get(reverse("resource_admin_database"), {"status": Post.STATUS_DRAFT})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, draft_post.title)
        self.assertNotContains(response, published_post.title)

    def test_database_page_can_paginate_and_sort_posts(self):
        self.client.login(username="staffuser", password="strong-password-123")
        for index in range(12):
            Post.objects.create(
                title=f"Post {index:02d}",
                slug=f"post-{index:02d}",
                overview="Mo ta",
                content="Noi dung",
                author=self.author,
                thumbnail=SimpleUploadedFile(f"thumb-{index}.gif", TEST_GIF_BYTES, content_type="image/gif"),
                featured=False,
            )

        response = self.client.get(reverse("resource_admin_database"), {"sort": "title", "page": 2})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Page 2 / 2")
        self.assertContains(response, "Post 10")
        self.assertContains(response, "Post 11")
        self.assertNotContains(response, "Post 00")

    def test_database_page_can_paginate_comments(self):
        self.client.login(username="staffuser", password="strong-password-123")
        post = Post.objects.create(
            title="Post with comments",
            slug="post-with-comments",
            overview="Mo ta",
            content="Noi dung",
            author=self.author,
            thumbnail=SimpleUploadedFile("comments.gif", TEST_GIF_BYTES, content_type="image/gif"),
            featured=False,
        )
        for index in range(12):
            post.comments.create(author_name=f"Guest {index:02d}", body="Binh luan")

        response = self.client.get(reverse("resource_admin_database"), {"comment_page": 2})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Page 2 / 2")
        self.assertContains(response, "Guest 01")
        self.assertContains(response, "Guest 00")
        self.assertNotContains(response, "Guest 11")

    def test_duplicate_post_creates_draft_copy(self):
        self.client.login(username="staffuser", password="strong-password-123")
        category = Category.objects.create(
            title="Learn",
            subtitle="Study notes",
            slug="learn",
            thumbnail=SimpleUploadedFile("learn2.gif", TEST_GIF_BYTES, content_type="image/gif"),
        )
        source_post = Post.objects.create(
            title="Original post",
            slug="original-post",
            overview="Mo ta",
            content="Noi dung",
            author=self.author,
            thumbnail=SimpleUploadedFile("original.gif", TEST_GIF_BYTES, content_type="image/gif"),
            featured=True,
            status=Post.STATUS_PUBLISHED,
        )
        source_post.categories.add(category)

        response = self.client.get(reverse("post_duplicate", args=[source_post.id]))

        self.assertEqual(response.status_code, 302)
        duplicated_post = Post.objects.exclude(pk=source_post.pk).get()
        self.assertEqual(duplicated_post.status, Post.STATUS_DRAFT)
        self.assertTrue(duplicated_post.slug.startswith("original-post-copy"))
        self.assertEqual(list(duplicated_post.categories.all()), [category])

    def test_public_pages_only_show_published_posts(self):
        category = Category.objects.create(
            title="Learn Nihongo",
            subtitle="Study",
            slug="learn-nihongo",
            thumbnail=SimpleUploadedFile("learn-public.gif", TEST_GIF_BYTES, content_type="image/gif"),
        )
        published_post = Post.objects.create(
            title="Published title",
            slug="published-title",
            overview="Mo ta",
            content="Noi dung",
            author=self.author,
            thumbnail=SimpleUploadedFile("published-public.gif", TEST_GIF_BYTES, content_type="image/gif"),
            featured=True,
            status=Post.STATUS_PUBLISHED,
        )
        published_post.categories.add(category)
        draft_post = Post.objects.create(
            title="Draft title",
            slug="draft-title",
            overview="Mo ta nhap",
            content="Noi dung nhap",
            author=self.author,
            thumbnail=SimpleUploadedFile("draft-public.gif", TEST_GIF_BYTES, content_type="image/gif"),
            featured=True,
            status=Post.STATUS_DRAFT,
        )
        draft_post.categories.add(category)

        homepage_response = self.client.get(reverse("homepage"))
        allposts_response = self.client.get(reverse("allposts"))
        postlist_response = self.client.get(reverse("postlist", args=[category.slug]))
        post_response = self.client.get(reverse("post", args=[published_post.slug]))
        draft_post_response = self.client.get(reverse("post", args=[draft_post.slug]))

        self.assertContains(homepage_response, published_post.title)
        self.assertNotContains(homepage_response, draft_post.title)
        self.assertContains(allposts_response, published_post.title)
        self.assertNotContains(allposts_response, draft_post.title)
        self.assertContains(postlist_response, published_post.title)
        self.assertNotContains(postlist_response, draft_post.title)
        self.assertEqual(post_response.status_code, 200)
        self.assertEqual(draft_post_response.status_code, 404)

    def test_post_form_rejects_duplicate_slug(self):
        self.client.login(username="staffuser", password="strong-password-123")
        category = Category.objects.create(
            title="Learn",
            subtitle="Study notes",
            slug="learn",
            thumbnail=SimpleUploadedFile("learn.jpg", b"image-bytes", content_type="image/jpeg"),
        )
        Post.objects.create(
            title="Bai cu",
            slug="slug-trung",
            overview="Mo ta",
            content="Noi dung",
            author=self.author,
            thumbnail=SimpleUploadedFile("thumb-old.gif", TEST_GIF_BYTES, content_type="image/gif"),
            featured=False,
        ).categories.add(category)

        response = self.client.post(
            reverse("post_create"),
            {
                "title": "Bai moi",
                "slug": "slug-trung",
                "overview": "Mo ta moi",
                "content": "Noi dung moi",
                "author_name": "Sensei Hana",
                "categories": [category.id],
                "status": Post.STATUS_PUBLISHED,
                "thumbnail": SimpleUploadedFile("thumb-new.gif", TEST_GIF_BYTES, content_type="image/gif"),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Slug nay da ton tai")

    def test_post_view_uses_latest_post_when_slug_is_duplicated(self):
        older_post = Post.objects.create(
            title="Bai cu",
            slug="slug-bi-trung",
            overview="Mo ta cu",
            content="Noi dung cu",
            author=self.author,
            thumbnail=SimpleUploadedFile("old.gif", TEST_GIF_BYTES, content_type="image/gif"),
            featured=False,
        )
        newer_post = Post.objects.create(
            title="Bai moi",
            slug="slug-bi-trung",
            overview="Mo ta moi",
            content="Noi dung moi",
            author=self.author,
            thumbnail=SimpleUploadedFile("new.gif", TEST_GIF_BYTES, content_type="image/gif"),
            featured=False,
        )

        response = self.client.get(reverse("post", args=["slug-bi-trung"]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, newer_post.title)
        self.assertNotContains(response, older_post.title)
