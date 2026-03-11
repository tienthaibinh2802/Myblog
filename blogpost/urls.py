from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
import os

from posts.views import (
    ResourceAdminLoginView,
    ResourceAdminLogoutView,
    allposts,
    about,
    category_create,
    category_delete,
    category_update,
    comment_delete,
    homepage,
    post,
    post_create,
    post_delete,
    post_update,
    postlist,
    resource_admin_database,
    resource_admin_dashboard,
    resource_group_create,
    resource_group_delete,
    resource_group_update,
    resource_library,
    resource_link_create,
    resource_link_delete,
    resource_link_update,
    resource_section_create,
    resource_section_delete,
    resource_section_update,
    search,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage, name = 'homepage'),
    path('post/<slug>/', post, name = 'post'),
    path('about/', about,name = 'about' ),
    path('search/', search, name = 'search'),
    path('postlist/<slug>/', postlist, name = 'postlist'), 
    path('posts/', allposts, name = 'allposts'),
    path('resources/', resource_library, name='resource_library'),
    path('sql/login/', ResourceAdminLoginView.as_view(), name='resource_admin_login'),
    path('sql/logout/', ResourceAdminLogoutView.as_view(), name='resource_admin_logout'),
    path('sql/', resource_admin_dashboard, name='resource_admin_dashboard'),
    path('sql/database/', resource_admin_database, name='resource_admin_database'),
    path('sql/categories/create/', category_create, name='category_create'),
    path('sql/categories/<int:pk>/edit/', category_update, name='category_update'),
    path('sql/categories/<int:pk>/delete/', category_delete, name='category_delete'),
    path('sql/posts/create/', post_create, name='post_create'),
    path('sql/posts/<int:pk>/edit/', post_update, name='post_update'),
    path('sql/posts/<int:pk>/delete/', post_delete, name='post_delete'),
    path('sql/comments/<int:pk>/delete/', comment_delete, name='comment_delete'),
    path('sql/sections/create/', resource_section_create, name='resource_section_create'),
    path('sql/sections/<int:pk>/edit/', resource_section_update, name='resource_section_update'),
    path('sql/sections/<int:pk>/delete/', resource_section_delete, name='resource_section_delete'),
    path('sql/groups/create/', resource_group_create, name='resource_group_create'),
    path('sql/groups/<int:pk>/edit/', resource_group_update, name='resource_group_update'),
    path('sql/groups/<int:pk>/delete/', resource_group_delete, name='resource_group_delete'),
    path('sql/links/create/', resource_link_create, name='resource_link_create'),
    path('sql/links/<int:pk>/edit/', resource_link_update, name='resource_link_update'),
    path('sql/links/<int:pk>/delete/', resource_link_delete, name='resource_link_delete'),
    
]

if settings.DEBUG or os.getenv("RENDER", "").lower() == "true":
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
