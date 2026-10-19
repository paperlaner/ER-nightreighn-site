from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from books import views as book_views
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("hello/", views.hello, name="hello"),
    path("index/", views.index_page, name="index"),
    path("index/<str:name>/", views.index_page, name="index_with_name"),
    path("feedback/", views.feedback_view, name="feedback"),
    path("feedback/success/", views.feedback_success, name="feedback_success"),
    path("status-json/", views.status_json, name="status_json"),
    path("about/", views.AboutPageView.as_view(), name="about"),
    path("template-demo/", views.template_demo, name="template_demo"),
    path("template-nested/", views.template_nested, name="template_nested"),
    path("main-url/", views.main_page_address, name="main_page_address"),
    path("home/", RedirectView.as_view(pattern_name="books:home", permanent=False), name="home_redirect"),
    path("blog/", include("blog.urls")),
    path("preview/404/", views.preview_page_not_found, name="preview_404"),
    re_path(r"^digits/(?P<value>\d+)/$", views.numeric_only_view, name="digits_only"),
    path("<int:pk>/", book_views.book_detail_shortcut, name="book_detail_shortcut_root"),
    path("", include("books.urls")),
    path("users/", include("users.urls")),
]

handler404 = "library_project.views.custom_page_not_found"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    re_path(r"^(?P<unmatched>.*)$", views.custom_page_not_found_fallback),
]
