from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField()

    def __str__(self):
        return self.user.username

class Category(models.Model):
    title = models.CharField(max_length=20)
    subtitle = models.CharField(max_length=20)
    slug = models.SlugField()
    thumbnail = models.ImageField()

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    overview = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    thumbnail = models.ImageField()
    categories = models.ManyToManyField(Category)
    featured = models.BooleanField()

    def __str__(self):
        return self.title


class ResourceSection(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "title"]

    def __str__(self):
        return self.title


class ResourceGroup(models.Model):
    section = models.ForeignKey(
        ResourceSection,
        on_delete=models.CASCADE,
        related_name="groups",
    )
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "title"]
        unique_together = ("section", "title")

    def __str__(self):
        return f"{self.section.title} - {self.title}"


class ResourceLink(models.Model):
    group = models.ForeignKey(
        ResourceGroup,
        on_delete=models.CASCADE,
        related_name="links",
    )
    title = models.CharField(max_length=150)
    url = models.URLField(blank=True)
    document = models.FileField(upload_to="resources/files/", blank=True)
    note = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "title"]
        unique_together = ("group", "title")

    def clean(self):
        if not self.url and not self.document:
            raise ValidationError("Please provide either a URL or an uploaded file.")
        if self.url and not self.url.startswith(("http://", "https://")):
            raise ValidationError({"url": "Link phai bat dau bang http:// hoac https://"})

    def __str__(self):
        return self.title


