from .retriever import SimilaritySearchRetriever


class BookRecommendationService:
    """Recommend related books from vector similarity over indexed book chunks."""

    def __init__(self, retriever=None):
        self.retriever = retriever or SimilaritySearchRetriever()

    def recommend(self, book, top_k=5, search_k=20):
        query_text = " ".join(
            part for part in [book.title, book.author, book.genre, book.summary, book.description] if part
        ).strip()
        if not query_text:
            return []

        retrieved_chunks = self.retriever.search(question=query_text, top_k=search_k)
        recommendations = []
        seen_book_ids = set([str(getattr(book, "id", ""))])

        for chunk in retrieved_chunks:
            metadata = chunk.metadata or {}
            related_book_id = str(metadata.get("book_id", ""))
            if not related_book_id or related_book_id in seen_book_ids:
                continue

            seen_book_ids.add(related_book_id)
            recommendations.append(
                {
                    "book_id": int(related_book_id) if related_book_id.isdigit() else related_book_id,
                    "title": metadata.get("book_title", "Unknown Book"),
                    "author": metadata.get("book_author", "Unknown Author"),
                    "url": metadata.get("book_url", ""),
                    "score": round(chunk.score, 3),
                    "reason": chunk.text,
                }
            )

            if len(recommendations) >= top_k:
                break

        return recommendations