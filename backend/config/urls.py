"""URL configuration for the project."""

from django.contrib import admin
from django.urls import include, path

from books.views import BookAskAPIView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ask/", BookAskAPIView.as_view(), name="book-ask"),
    path("api/books/", include("books.urls")),
]
