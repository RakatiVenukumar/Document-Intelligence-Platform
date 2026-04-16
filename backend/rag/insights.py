import re

from .llm import ChatLLMClient


class BookInsightService:
    """Generate and persist book summary and genre insights."""

    GENRE_KEYWORDS = {
        "Science Fiction": ["space", "robot", "alien", "future", "technology", "science"],
        "Fantasy": ["magic", "dragon", "quest", "kingdom", "wizard", "realm"],
        "Mystery": ["murder", "detective", "investigation", "clue", "mystery", "crime"],
        "Romance": ["love", "relationship", "heart", "romance", "wedding"],
        "Thriller": ["chase", "danger", "spy", "secret", "thriller", "suspense"],
        "Self-Help": ["habits", "productivity", "mindset", "growth", "success", "improve"],
        "Biography": ["life", "memoir", "autobiography", "journey", "story of"],
        "History": ["history", "war", "civilization", "historical", "past", "century"],
        "Business": ["business", "leadership", "strategy", "startup", "finance", "management"],
    }

    def __init__(self, llm_client=None):
        self.llm_client = llm_client or ChatLLMClient()

    def generate_summary(self, book):
        prompt = (
            "Write a concise 2-3 sentence summary of this book using the title, author, and description. "
            "Keep it clear, factual, and useful for a reader deciding whether to read it."
        )
        context = self._compose_context(book)
        try:
            return self.llm_client.complete(prompt, context).strip()
        except Exception:
            return self._fallback_summary(book)

    def classify_genre(self, book):
        prompt = (
            "Classify the book into one genre from this list only: "
            "Fantasy, Science Fiction, Mystery, Romance, Thriller, Self-Help, Biography, History, Business, Other. "
            "Respond with only the genre label."
        )
        context = self._compose_context(book)
        try:
            raw_genre = self.llm_client.complete(prompt, context).strip()
            return self._normalize_genre(raw_genre)
        except Exception:
            return self._fallback_genre(book)

    def generate_insights(self, book, persist=True):
        summary = self.generate_summary(book)
        genre = self.classify_genre(book)

        if persist:
            book.summary = summary
            book.genre = genre
            book.save(update_fields=["summary", "genre"])

        return {"summary": summary, "genre": genre}

    def _compose_context(self, book):
        return "\n".join(
            part for part in [
                f"Title: {book.title}",
                f"Author: {book.author}",
                f"Description: {book.description}",
            ]
            if part
        )

    def _fallback_summary(self, book):
        description = (book.description or "").strip()
        if not description:
            return f"{book.title} by {book.author} is a book in the catalog."

        sentences = re.split(r"(?<=[.!?])\s+", description)
        summary = " ".join(sentences[:2]).strip()
        return summary[:280]

    def _fallback_genre(self, book):
        text = f"{book.title} {book.description}".lower()
        best_genre = "Other"
        best_score = 0

        for genre, keywords in self.GENRE_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > best_score:
                best_score = score
                best_genre = genre

        return best_genre

    def _normalize_genre(self, genre_label):
        cleaned = genre_label.strip().lower()
        allowed = {
            "fantasy": "Fantasy",
            "science fiction": "Science Fiction",
            "mystery": "Mystery",
            "romance": "Romance",
            "thriller": "Thriller",
            "self-help": "Self-Help",
            "biography": "Biography",
            "history": "History",
            "business": "Business",
            "other": "Other",
        }
        return allowed.get(cleaned, "Other")