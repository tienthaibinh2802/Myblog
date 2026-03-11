from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Author, Category, Comment, Post, ResourceGroup, ResourceLink, ResourceSection


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
    author = forms.ModelChoiceField(
        queryset=Author.objects.select_related("user"),
        widget=forms.Select(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
    )
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3 min-h-[160px]"}),
    )

    class Meta:
        model = Post
        fields = ["title", "slug", "overview", "content", "author", "thumbnail", "categories", "featured"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
            "slug": forms.TextInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
            "overview": forms.Textarea(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3 min-h-[120px]"}),
            "content": forms.Textarea(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3 min-h-[240px]"}),
            "thumbnail": forms.ClearableFileInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
            "featured": forms.CheckboxInput(attrs={"class": "h-5 w-5 rounded border-slate-300 text-pink-500 focus:ring-pink-500"}),
        }


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
