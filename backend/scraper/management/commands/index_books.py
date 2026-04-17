from django.core.management.base import BaseCommand

from books.models import Book
from rag.indexer import BookEmbeddingIndexer

class Command(BaseCommand):
    help = "Index all books in the database for RAG pipeline (chunking, embedding, and storing in vector DB)."

    def handle(self, *args, **options):
        indexer = BookEmbeddingIndexer()
        books = Book.objects.all()
        self.stdout.write(f"Indexing {books.count()} books...")
        indexed_ids = indexer.index_books(books)
        self.stdout.write(self.style.SUCCESS(f"Indexed {len(indexed_ids)} chunks for {books.count()} books."))
