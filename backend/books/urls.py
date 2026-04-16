from django.urls import path

from .views import BookDetailAPIView, BookListAPIView, BookRecommendationsAPIView, BookUploadAPIView

urlpatterns = [
	path("", BookListAPIView.as_view(), name="book-list"),
	path("upload-book/", BookUploadAPIView.as_view(), name="book-upload"),
	path("<int:pk>/related/", BookRecommendationsAPIView.as_view(), name="book-related"),
	path("<int:pk>/", BookDetailAPIView.as_view(), name="book-detail"),
]
