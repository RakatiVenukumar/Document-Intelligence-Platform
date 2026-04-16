from functools import lru_cache

from sentence_transformers import SentenceTransformer


class SentenceTransformerEmbedder:
    """Generate normalized embeddings for book chunks and questions."""

    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model_name = model_name

    @property
    @lru_cache(maxsize=1)
    def model(self):
        return SentenceTransformer(self.model_name)

    def embed_texts(self, texts):
        if not texts:
            return []

        vectors = self.model.encode(list(texts), normalize_embeddings=True)
        if len(texts) == 1:
            return [vectors.tolist()]

        return [vector.tolist() for vector in vectors]

    def embed_text(self, text):
        return self.embed_texts([text])[0]