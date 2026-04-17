from .chunking import TextChunker
from .embeddings import SentenceTransformerEmbedder
from .retriever import SimilaritySearchRetriever
from .store import ChromaVectorStore


class BookEmbeddingIndexer:
    """Chunk books, embed them, and persist vectors in ChromaDB."""

    def __init__(self, chunker=None, embedder=None, store=None):
        self.chunker = chunker or TextChunker()
        self.embedder = embedder or SentenceTransformerEmbedder()
        self.store = store or ChromaVectorStore()

    def index_book(self, book):
        source_text = " ".join(
            part for part in [book.title, book.author, book.description] if part
        ).strip()
        chunks = self.chunker.chunk_text(source_text)
        if not chunks:
            return []

        documents = [chunk.text for chunk in chunks]
        embeddings = self.embedder.embed_texts(documents)
        # Fix: flatten embeddings if shape is [[[...]]] instead of [[...]]
        if len(embeddings) == 1 and isinstance(embeddings[0], list) and isinstance(embeddings[0][0], list):
            embeddings = embeddings[0]

        ids = [f"book-{book.id}-chunk-{chunk.index}" for chunk in chunks]
        metadatas = [
            {
                "book_id": str(book.id),
                "book_title": book.title,
                "book_author": book.author,
                "book_url": book.url,
                "chunk_index": chunk.index,
                "start_word": chunk.start_word,
                "end_word": chunk.end_word,
            }
            for chunk in chunks
        ]

        self.store.upsert_chunks(ids, documents, embeddings, metadatas)
        return ids

    def index_books(self, books):
        indexed_ids = []
        for book in books:
            indexed_ids.extend(self.index_book(book))
        return indexed_ids


class BookSimilarityService:
    """Public service for querying indexed book chunks."""

    def __init__(self, retriever=None):
        self.retriever = retriever or SimilaritySearchRetriever()

    def search(self, question, book_id=None, top_k=5):
        return self.retriever.search(question=question, book_id=book_id, top_k=top_k)