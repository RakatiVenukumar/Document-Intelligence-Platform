from dataclasses import dataclass
from typing import Dict, List, Optional

from .embeddings import SentenceTransformerEmbedder
from .store import ChromaVectorStore


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    text: str
    score: float
    metadata: Dict[str, object]


class SimilaritySearchRetriever:
    """Find the most relevant stored chunks for a question."""

    def __init__(self, embedder=None, store=None):
        self.embedder = embedder or SentenceTransformerEmbedder()
        self.store = store or ChromaVectorStore()

    def search(self, question, book_id=None, top_k=5):
        question_embedding = self.embedder.embed_text(question)
        where = {"book_id": str(book_id)} if book_id is not None else None
        results = self.store.query(question_embedding, n_results=top_k, where=where)
        return self._format_results(results)

    def _format_results(self, results):
        if not results or not results.get("ids"):
            return []

        retrieved_chunks = []
        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for chunk_id, document, metadata, distance in zip(ids, documents, metadatas, distances):
            score = max(0.0, 1.0 - float(distance)) if distance is not None else 0.0
            retrieved_chunks.append(
                RetrievedChunk(
                    chunk_id=chunk_id,
                    text=document,
                    score=score,
                    metadata=metadata or {},
                )
            )

        return retrieved_chunks