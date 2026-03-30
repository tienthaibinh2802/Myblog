from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.core.paginator import Paginator
from django.db.models import Q 
from django.http import Http404
from django.utils.text import slugify
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    AdminLoginForm,
    CategoryForm,
    CommentForm,
    PostForm,
    ResourceGroupForm,
    ResourceLinkForm,
    ResourceSectionForm,
)
from .models import Author, Category, Comment, Post, ResourceGroup, ResourceLink, ResourceSection


def staff_required(view_func):
    @wraps(view_func)
    @login_required(login_url="resource_admin_login")
    @user_passes_test(
        lambda user: user.is_staff or user.is_superuser,
        login_url="resource_admin_login",
    )
    def _wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)

    return _wrapped_view

def get_author(user):
    qs = Author.objects.filter(user=user)
    if qs.exists():
        return qs[0]
    return None


def published_posts():
    return Post.objects.filter(status=Post.STATUS_PUBLISHED)


def build_unique_post_slug(base_value):
    base_slug = slugify(base_value) or "post-copy"
    slug = base_slug
    counter = 2
    while Post.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug

def homepage (request):
    categories = Category.objects.all()[0:3]
    featured = published_posts().filter(featured=True)
    latest = published_posts().order_by('-timestamp')[0:6]
    resource_sections = ResourceSection.objects.prefetch_related('groups__links')[:3]
    context= {
        'object_list': featured,
        'latest': latest,
        'categories':categories,
        'resource_sections': resource_sections,
    }
    return render(request, 'homepage.html',context)

def post (request,slug):
    post = published_posts().filter(slug=slug).order_by("-timestamp", "-id").first()
    if not post:
        raise Http404()
    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
            messages.success(request, "Comment da duoc gui.")
            return redirect("post", slug=slug)
    else:
        comment_form = CommentForm()

    latest = published_posts().order_by('-timestamp')[:3]
    comments = post.comments.all()
    context = {
        'post': post,
        'latest': latest,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'post.html', context)

def about (request):
    return render(request, 'about_page.html')

def search(request):
    queryset = published_posts()
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(overview__icontains=query)
        ).distinct()
    context = {
        'object_list': queryset
    }
    return render(request, 'search_bar.html', context)


def postlist (request,slug):
    category = get_object_or_404(Category, slug=slug)
    posts = published_posts().filter(categories__in=[category])

    context = {
        'posts': posts,
        'category': category,
    }
    return render(request, 'post_list.html', context)

def allposts(request):
    posts = published_posts().order_by('-timestamp')

    context = {
        'posts': posts,
    }
    return render(request, 'all_posts.html', context)


def resource_library(request):
    sections = ResourceSection.objects.prefetch_related('groups__links')
    context = {
        'sections': sections,
    }
    return render(request, 'resource_library.html', context)


class ResourceAdminLoginView(LoginView):
    template_name = "resource_admin/login.html"
    authentication_form = AdminLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return "/sql/"


class ResourceAdminLogoutView(LogoutView):
    next_page = "/sql/login/"


@staff_required
def resource_admin_dashboard(request):
    sections = ResourceSection.objects.prefetch_related("groups__links")
    categories = Category.objects.order_by("title")
    posts = Post.objects.select_related("author").prefetch_related("categories").order_by("-timestamp")[:8]
    comments = Comment.objects.select_related("post").order_by("-created_at")[:10]
    context = {
        "sections": sections,
        "categories": categories,
        "posts": posts,
        "comments": comments,
        "section_count": ResourceSection.objects.count(),
        "group_count": ResourceGroup.objects.count(),
        "link_count": ResourceLink.objects.count(),
        "category_count": Category.objects.count(),
        "post_count": Post.objects.count(),
        "comment_count": Comment.objects.count(),
    }
    return render(request, "resource_admin/dashboard.html", context)


@staff_required
def resource_admin_database(request):
    query = request.GET.get("q", "").strip()
    selected_section = request.GET.get("section", "").strip()
    selected_category = request.GET.get("category", "").strip()
    featured_filter = request.GET.get("featured", "").strip()
    status_filter = request.GET.get("status", "").strip()
    sort = request.GET.get("sort", "-timestamp").strip() or "-timestamp"
    comment_sort = request.GET.get("comment_sort", "-created_at").strip() or "-created_at"

    sections = ResourceSection.objects.prefetch_related("groups__links")
    groups = ResourceGroup.objects.select_related("section")
    links = ResourceLink.objects.select_related("group", "group__section")
    categories = Category.objects.order_by("title")
    posts = Post.objects.select_related("author").prefetch_related("categories").order_by("-timestamp")
    comments = Comment.objects.select_related("post").order_by("-created_at")

    if selected_section:
        sections = sections.filter(id=selected_section)
        groups = groups.filter(section_id=selected_section)
        links = links.filter(group__section_id=selected_section)

    if query:
        sections = sections.filter(
            Q(title__icontains=query) | Q(slug__icontains=query) | Q(description__icontains=query)
        )
        groups = groups.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(section__title__icontains=query)
        )
        links = links.filter(
            Q(title__icontains=query)
            | Q(url__icontains=query)
            | Q(note__icontains=query)
            | Q(group__title__icontains=query)
            | Q(group__section__title__icontains=query)
        )
        categories = categories.filter(
            Q(title__icontains=query) | Q(subtitle__icontains=query) | Q(slug__icontains=query)
        )
        posts = posts.filter(
            Q(title__icontains=query)
            | Q(slug__icontains=query)
            | Q(overview__icontains=query)
            | Q(content__icontains=query)
            | Q(author__display_name__icontains=query)
            | Q(author__user__username__icontains=query)
            | Q(categories__title__icontains=query)
            | Q(categories__subtitle__icontains=query)
        ).distinct()
        comments = comments.filter(
            Q(author_name__icontains=query)
            | Q(body__icontains=query)
            | Q(post__title__icontains=query)
        )

    if selected_category:
        posts = posts.filter(categories__id=selected_category)

    if featured_filter == "yes":
        posts = posts.filter(featured=True)
    elif featured_filter == "no":
        posts = posts.filter(featured=False)

    if status_filter in {Post.STATUS_DRAFT, Post.STATUS_PUBLISHED}:
        posts = posts.filter(status=status_filter)

    sort_options = {
        "-timestamp": ("-timestamp", "-id"),
        "timestamp": ("timestamp", "id"),
        "title": ("title", "id"),
        "-title": ("-title", "-id"),
        "author": ("author__display_name", "author__user__username", "id"),
        "-author": ("-author__display_name", "-author__user__username", "-id"),
    }
    posts = posts.order_by(*sort_options.get(sort, ("-timestamp", "-id"))).distinct()
    post_paginator = Paginator(posts, 10)
    post_page = post_paginator.get_page(request.GET.get("page"))
    comment_sort_options = {
        "-created_at": ("-created_at", "-id"),
        "created_at": ("created_at", "id"),
        "author_name": ("author_name", "id"),
        "-author_name": ("-author_name", "-id"),
    }
    comments = comments.order_by(*comment_sort_options.get(comment_sort, ("-created_at", "-id")))
    comment_paginator = Paginator(comments, 10)
    comment_page = comment_paginator.get_page(request.GET.get("comment_page"))

    context = {
        "sections": sections,
        "groups": groups,
        "links": links,
        "categories": categories,
        "posts": post_page,
        "comments": comment_page,
        "query": query,
        "selected_section": selected_section,
        "selected_category": selected_category,
        "featured_filter": featured_filter,
        "status_filter": status_filter,
        "sort": sort,
        "comment_sort": comment_sort,
        "sort_options": [
            {"value": "-timestamp", "label": "Newest first"},
            {"value": "timestamp", "label": "Oldest first"},
            {"value": "title", "label": "Title A-Z"},
            {"value": "-title", "label": "Title Z-A"},
            {"value": "author", "label": "Author A-Z"},
            {"value": "-author", "label": "Author Z-A"},
        ],
        "comment_sort_options": [
            {"value": "-created_at", "label": "Newest comments"},
            {"value": "created_at", "label": "Oldest comments"},
            {"value": "author_name", "label": "Author A-Z"},
            {"value": "-author_name", "label": "Author Z-A"},
        ],
        "status_options": [
            {"value": "", "label": "All statuses"},
            {"value": Post.STATUS_PUBLISHED, "label": "Published only"},
            {"value": Post.STATUS_DRAFT, "label": "Draft only"},
        ],
        "all_sections": ResourceSection.objects.all(),
        "all_categories": Category.objects.order_by("title"),
    }
    return render(request, "resource_admin/database.html", context)


@staff_required
def resource_section_create(request):
    form = ResourceSectionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Section created successfully.")
        return redirect("resource_admin_dashboard")
    return render(
        request,
        "resource_admin/section_form.html",
        {"form": form, "page_title": "Create section"},
    )


@staff_required
def resource_section_update(request, pk):
    section = get_object_or_404(ResourceSection, pk=pk)
    form = ResourceSectionForm(request.POST or None, instance=section)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Section updated successfully.")
        return redirect("resource_admin_dashboard")
    return render(
        request,
        "resource_admin/section_form.html",
        {"form": form, "page_title": f"Edit section: {section.title}", "section": section},
    )


@staff_required
def resource_section_delete(request, pk):
    section = get_object_or_404(ResourceSection, pk=pk)
    if request.method == "POST":
        section.delete()
        messages.success(request, "Section deleted successfully.")
        return redirect("resource_admin_dashboard")
    return render(
        request,
        "resource_admin/confirm_delete.html",
        {
            "object_name": section.title,
            "cancel_url": "/sql/",
            "page_title": "Delete section",
        },
    )


@staff_required
def resource_group_create(request):
    initial = {}
    section_id = request.GET.get("section")
    if section_id:
        initial["section"] = section_id
    form = ResourceGroupForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Group created successfully.")
        return redirect("resource_admin_dashboard")
    return render(
        request,
        "resource_admin/group_form.html",
        {"form": form, "page_title": "Create group"},
    )


@staff_required
def resource_group_update(request, pk):
    group = get_object_or_404(ResourceGroup, pk=pk)
    form = ResourceGroupForm(request.POST or None, instance=group)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Group updated successfully.")
        return redirect("resource_admin_dashboard")
    return render(
        request,
        "resource_admin/group_form.html",
        {"form": form, "page_title": f"Edit group: {group.title}", "group": group},
    )


@staff_required
def resource_group_delete(request, pk):
    group = get_object_or_404(ResourceGroup, pk=pk)
    if request.method == "POST":
        group.delete()
        messages.success(request, "Group deleted successfully.")
        return redirect("resource_admin_dashboard")
    return render(
        request,
        "resource_admin/confirm_delete.html",
        {
            "object_name": group.title,
            "cancel_url": "/sql/",
            "page_title": "Delete group",
        },
    )


@staff_required
def resource_link_create(request):
    initial = {}
    group_id = request.GET.get("group")
    if group_id:
        initial["group"] = group_id
    form = ResourceLinkForm(request.POST or None, request.FILES or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Link created successfully.")
        return redirect("resource_admin_dashboard")
    return render(
        request,
        "resource_admin/link_form.html",
        {"form": form, "page_title": "Create link"},
    )


@staff_required
def resource_link_update(request, pk):
    link = get_object_or_404(ResourceLink, pk=pk)
    form = ResourceLinkForm(request.POST or None, request.FILES or None, instance=link)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Link updated successfully.")
        return redirect("resource_admin_dashboard")
    return render(
        request,
        "resource_admin/link_form.html",
        {"form": form, "page_title": f"Edit link: {link.title}", "link": link},
    )


@staff_required
def resource_link_delete(request, pk):
    link = get_object_or_404(ResourceLink, pk=pk)
    if request.method == "POST":
        link.delete()
        messages.success(request, "Link deleted successfully.")
        return redirect("resource_admin_dashboard")
    return render(
        request,
        "resource_admin/confirm_delete.html",
        {
            "object_name": link.title,
            "cancel_url": "/sql/",
            "page_title": "Delete link",
        },
    )


@staff_required
def category_create(request):
    form = CategoryForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Category created successfully.")
        return redirect("resource_admin_dashboard")
    return render(
        request,
        "resource_admin/category_form.html",
        {"form": form, "page_title": "Create category"},
    )


@staff_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, request.FILES or None, instance=category)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Category updated successfully.")
        return redirect("resource_admin_dashboard")
    return render(
        request,
        "resource_admin/category_form.html",
        {"form": form, "page_title": f"Edit category: {category.title}", "category": category},
    )


@staff_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted successfully.")
        return redirect("resource_admin_dashboard")
    return render(
        request,
        "resource_admin/confirm_delete.html",
        {
            "object_name": category.title,
            "cancel_url": "/sql/",
            "page_title": "Delete category",
        },
    )


@staff_required
def post_create(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Post created successfully.")
        return redirect("resource_admin_dashboard")
    return render(
        request,
        "resource_admin/post_form.html",
        {"form": form, "page_title": "Create post"},
    )


@staff_required
def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Post updated successfully.")
        return redirect("resource_admin_dashboard")
    return render(
        request,
        "resource_admin/post_form.html",
        {"form": form, "page_title": f"Edit post: {post.title}", "post": post},
    )


@staff_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted successfully.")
        return redirect("resource_admin_dashboard")
    return render(
        request,
        "resource_admin/confirm_delete.html",
        {
            "object_name": post.title,
            "cancel_url": "/sql/",
            "page_title": "Delete post",
        },
    )


@staff_required
def post_duplicate(request, pk):
    source_post = get_object_or_404(Post.objects.prefetch_related("categories"), pk=pk)
    duplicated_post = Post.objects.create(
        title=f"{source_post.title} Copy",
        slug=build_unique_post_slug(f"{source_post.slug}-copy"),
        overview=source_post.overview,
        content=source_post.content,
        author=source_post.author,
        thumbnail=source_post.thumbnail,
        featured=source_post.featured,
        status=Post.STATUS_DRAFT,
    )
    duplicated_post.categories.set(source_post.categories.all())
    messages.success(request, "Post duplicated as draft.")
    return redirect("post_update", pk=duplicated_post.pk)


@staff_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.method == "POST":
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
        return redirect("resource_admin_dashboard")
    return render(
        request,
        "resource_admin/confirm_delete.html",
        {
            "object_name": f"Comment by {comment.author_name}",
            "cancel_url": "/sql/",
            "page_title": "Delete comment",
        },
    )
