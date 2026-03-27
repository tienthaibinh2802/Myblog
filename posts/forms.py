from django import forms
from django.db.models import Q
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from .models import Author, Category, Comment, Post, ResourceGroup, ResourceLink, ResourceSection

User = get_user_model()


class AdminLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
    )


class ResourceSectionForm(forms.ModelForm):
    class Meta:
        model = ResourceSection
        fields = ["title", "slug", "description", "display_order"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
            "slug": forms.TextInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
            "description": forms.Textarea(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3 min-h-[120px]"}),
            "display_order": forms.NumberInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
        }


class ResourceGroupForm(forms.ModelForm):
    class Meta:
        model = ResourceGroup
        fields = ["section", "title", "description", "display_order"]
        widgets = {
            "section": forms.Select(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
            "title": forms.TextInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
            "description": forms.Textarea(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3 min-h-[120px]"}),
            "display_order": forms.NumberInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
        }


class ResourceLinkForm(forms.ModelForm):
    class Meta:
        model = ResourceLink
        fields = ["group", "title", "url", "document", "note", "display_order"]
        widgets = {
            "group": forms.Select(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
            "title": forms.TextInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
            "url": forms.URLInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3", "placeholder": "https://"}),
            "document": forms.ClearableFileInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
            "note": forms.TextInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
            "display_order": forms.NumberInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["title", "subtitle", "slug", "thumbnail"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
            "subtitle": forms.TextInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
            "slug": forms.TextInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
            "thumbnail": forms.ClearableFileInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
        }


class PostForm(forms.ModelForm):
    author_name = forms.CharField(
        label="Author",
        widget=forms.TextInput(
            attrs={
                "class": "w-full rounded-xl border border-slate-300 px-4 py-3",
                "placeholder": "Nhap ten tac gia",
            }
        ),
    )
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3 min-h-[160px]"}),
    )

    class Meta:
        model = Post
        fields = ["title", "slug", "overview", "content", "thumbnail", "categories", "featured"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
            "slug": forms.TextInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
            "overview": forms.Textarea(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3 min-h-[120px]"}),
            "content": forms.Textarea(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3 min-h-[240px]"}),
            "thumbnail": forms.ClearableFileInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
            "featured": forms.CheckboxInput(attrs={"class": "h-5 w-5 rounded border-slate-300 text-pink-500 focus:ring-pink-500"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.author_id:
            self.fields["author_name"].initial = self.instance.author.display_name or self.instance.author.user.username

    def clean_slug(self):
        slug = self.cleaned_data["slug"].strip()
        queryset = Post.objects.filter(slug=slug)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("Slug nay da ton tai. Vui long nhap slug khac.")
        return slug

    def save(self, commit=True):
        post = super().save(commit=False)
        post.author = self._get_or_create_author(self.cleaned_data["author_name"])
        if commit:
            post.save()
            self.save_m2m()
        return post

    def _get_or_create_author(self, author_name):
        normalized_name = author_name.strip()
        existing_author = Author.objects.select_related("user").filter(
            Q(display_name__iexact=normalized_name) | Q(user__username__iexact=normalized_name)
        ).first()
        if existing_author:
            return existing_author

        base_username = slugify(normalized_name) or "author"
        username = base_username
        counter = 2
        while User.objects.filter(username=username).exists():
            username = f"{base_username}-{counter}"
            counter += 1

        user = User.objects.create(username=username)
        user.set_unusable_password()
        user.save(update_fields=["password"])
        return Author.objects.create(user=user, display_name=normalized_name)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["author_name", "body"]
        widgets = {
            "author_name": forms.TextInput(
                attrs={
                    "class": "w-full rounded-xl border border-rose-200 px-4 py-3",
                    "placeholder": "Ten cua ban",
                }
            ),
            "body": forms.Textarea(
                attrs={
                    "class": "w-full rounded-xl border border-rose-200 px-4 py-3 min-h-[110px]",
                    "placeholder": "Viet comment o day...",
                }
            ),
        }
