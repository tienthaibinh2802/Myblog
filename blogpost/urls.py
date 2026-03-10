from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from posts.views import (
    ResourceAdminLoginView,
    ResourceAdminLogoutView,
    allposts,
    about,
    homepage,
    post,
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
    path('sql/dang-nhap/', ResourceAdminLoginView.as_view(), name='resource_admin_login'),
    path('sql/dang-xuat/', ResourceAdminLogoutView.as_view(), name='resource_admin_logout'),
    path('sql/', resource_admin_dashboard, name='resource_admin_dashboard'),
    path('sql/database/', resource_admin_database, name='resource_admin_database'),
    path('sql/sections/them/', resource_section_create, name='resource_section_create'),
    path('sql/sections/<int:pk>/sua/', resource_section_update, name='resource_section_update'),
    path('sql/sections/<int:pk>/xoa/', resource_section_delete, name='resource_section_delete'),
    path('sql/groups/them/', resource_group_create, name='resource_group_create'),
    path('sql/groups/<int:pk>/sua/', resource_group_update, name='resource_group_update'),
    path('sql/groups/<int:pk>/xoa/', resource_group_delete, name='resource_group_delete'),
    path('sql/links/them/', resource_link_create, name='resource_link_create'),
    path('sql/links/<int:pk>/sua/', resource_link_update, name='resource_link_update'),
    path('sql/links/<int:pk>/xoa/', resource_link_delete, name='resource_link_delete'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
