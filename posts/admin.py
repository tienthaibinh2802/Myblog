from django.contrib import admin

from .models import Author, Category, Post, ResourceGroup, ResourceLink, ResourceSection

admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Post)


class ResourceGroupInline(admin.TabularInline):
    model = ResourceGroup
    extra = 1


@admin.register(ResourceSection)
class ResourceSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "display_order")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ResourceGroupInline]


class ResourceLinkInline(admin.TabularInline):
    model = ResourceLink
    extra = 1


@admin.register(ResourceGroup)
class ResourceGroupAdmin(admin.ModelAdmin):
    list_display = ("title", "section", "display_order")
    list_filter = ("section",)
    inlines = [ResourceLinkInline]


@admin.register(ResourceLink)
class ResourceLinkAdmin(admin.ModelAdmin):
    list_display = ("title", "group", "url", "display_order")
    list_filter = ("group__section", "group")
    search_fields = ("title", "note", "url")
