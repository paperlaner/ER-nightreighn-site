from django.urls import path

from . import views

app_name = "books"

urlpatterns = [
    path("", views.home, name="home"),
    path("cbv/books/", views.BookListPageView.as_view(), name="book_list_cbv"),
    path("cbv/books/<int:pk>/", views.BookDetailPageView.as_view(), name="book_detail_cbv"),
    path("cbv/authors/add/", views.AuthorCreatePageView.as_view(), name="author_create"),
    path("cbv/authors/<int:pk>/delete/", views.AuthorDeletePageView.as_view(), name="author_delete"),
    path("<int:pk>/", views.book_detail_shortcut, name="book_detail_shortcut"),
    path("books/", views.book_list, name="book_list"),
    path("books/add/", views.book_create, name="book_create"),
    path("books/search/<slug:slug>/", views.book_search_by_slug, name="book_search_by_slug"),
    path("books/<int:pk>/edit/", views.book_update, name="book_update"),
    path("books/<int:pk>/delete/", views.book_delete, name="book_delete"),
    path("books/<int:pk>/", views.book_detail, name="book_detail"),
    path("books/<int:pk>/favorite/", views.book_favorite_toggle, name="book_favorite"),
    path("nightlords/<slug:slug>/", views.nightlord_detail, name="nightlord_detail"),
    path("api/books/", views.api_book_list, name="api_book_list"),
    path("api/books/<int:pk>/", views.api_book_detail, name="api_book_detail"),
]
