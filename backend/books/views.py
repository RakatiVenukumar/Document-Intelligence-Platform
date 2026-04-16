from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Book
from .serializers import AskQuestionSerializer, BookSerializer
from rag.insights import BookInsightService
from rag.indexer import BookEmbeddingIndexer
from rag.recommendations import BookRecommendationService
from rag.pipeline import BookRAGPipeline


class BookListAPIView(generics.ListAPIView):
	queryset = Book.objects.all()
	serializer_class = BookSerializer


class BookDetailAPIView(generics.RetrieveAPIView):
	queryset = Book.objects.all()
	serializer_class = BookSerializer


class BookUploadAPIView(generics.CreateAPIView):
	queryset = Book.objects.all()
	serializer_class = BookSerializer

	def perform_create(self, serializer):
		book = serializer.save()
		BookInsightService().generate_insights(book, persist=True)
		try:
			BookEmbeddingIndexer().index_book(book)
		except Exception:
			pass


class BookRecommendationsAPIView(APIView):
	def get(self, request, pk):
		book = Book.objects.get(pk=pk)
		recommendations = BookRecommendationService().recommend(book)
		return Response(
			{
				"book_id": book.id,
				"recommendations": recommendations,
			},
			status=status.HTTP_200_OK,
		)


class BookAskAPIView(APIView):
	def post(self, request):
		serializer = AskQuestionSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		validated_data = serializer.validated_data
		pipeline = BookRAGPipeline()
		result = pipeline.answer(
			question=validated_data["question"],
			book_id=validated_data.get("book_id"),
			top_k=validated_data["top_k"],
		)
		return Response(result, status=status.HTTP_200_OK)
