from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import ResourceGroup, ResourceLink, ResourceSection


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
        fields = ["group", "title", "url", "note", "display_order"]
        widgets = {
            "group": forms.Select(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
            "title": forms.TextInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
            "url": forms.URLInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3", "placeholder": "https://"}),
            "note": forms.TextInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
            "display_order": forms.NumberInput(attrs={"class": "w-full rounded-xl border border-slate-300 px-4 py-3"}),
        }
