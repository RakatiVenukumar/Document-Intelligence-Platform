from rest_framework import serializers

from .models import Book


class BookSerializer(serializers.ModelSerializer):
	class Meta:
		model = Book
		fields = ["id", "title", "author", "description", "rating", "url", "summary", "genre"]


class AskQuestionSerializer(serializers.Serializer):
	question = serializers.CharField(max_length=1000)
	book_id = serializers.IntegerField(required=False, allow_null=True)
	top_k = serializers.IntegerField(required=False, default=5, min_value=1, max_value=10)
