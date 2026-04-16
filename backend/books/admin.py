from django.contrib import admin

from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
	list_display = ("title", "author", "rating", "url")
	search_fields = ("title", "author")
	list_filter = ("rating",)
