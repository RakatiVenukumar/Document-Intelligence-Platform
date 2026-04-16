from django.db import models


class Book(models.Model):
	title = models.CharField(max_length=255)
	author = models.CharField(max_length=255)
	description = models.TextField(blank=True, default="")
	rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
	url = models.URLField(max_length=500, unique=True)

	class Meta:
		ordering = ["title"]

	def __str__(self):
		return f"{self.title} by {self.author}"
