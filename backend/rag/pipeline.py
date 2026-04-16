from dataclasses import dataclass
from typing import Dict, List, Optional

from .indexer import BookSimilarityService
from .llm import ChatLLMClient


@dataclass(frozen=True)
class SourceChunk:
    citation_id: int
    chunk_id: str
    text: str
    score: float
    metadata: Dict[str, object]


class BookRAGPipeline:
    """Run question -> retrieve -> prompt -> answer with citations."""

    def __init__(self, retriever=None, llm_client=None):
        self.retriever = retriever or BookSimilarityService()
        self.llm_client = llm_client or ChatLLMClient()

    def answer(self, question, book_id=None, top_k=5):
        retrieved_chunks = self.retriever.search(question=question, book_id=book_id, top_k=top_k)
        source_chunks = self._number_sources(retrieved_chunks)

        if not source_chunks:
            return {
                "answer": "No relevant book context was found for this question.",
                "source_chunks": [],
                "used_llm": False,
            }

        context = self._build_context(source_chunks)
        citations = self._build_citations(source_chunks)

        try:
            answer = self.llm_client.generate(question=question, context=context, citations=citations)
            used_llm = True
        except Exception:
            answer = self._fallback_answer(question, source_chunks)
            used_llm = False

        return {
            "answer": answer,
            "source_chunks": [self._serialize_source(chunk) for chunk in source_chunks],
            "used_llm": used_llm,
        }

    def _number_sources(self, retrieved_chunks):
        source_chunks = []
        for index, chunk in enumerate(retrieved_chunks, start=1):
            source_chunks.append(
                SourceChunk(
                    citation_id=index,
                    chunk_id=chunk.chunk_id,
                    text=chunk.text,
                    score=chunk.score,
                    metadata=chunk.metadata,
                )
            )

        return source_chunks

    def _build_context(self, source_chunks):
        lines = []
        for chunk in source_chunks:
            book_title = chunk.metadata.get("book_title", "Unknown Book")
            lines.append(
                f"[{chunk.citation_id}] {book_title} | chunk {chunk.metadata.get('chunk_index', '?')} | {chunk.text}"
            )

        return "\n".join(lines)

    def _build_citations(self, source_chunks):
        return "\n".join(
            f"[{chunk.citation_id}] {chunk.metadata.get('book_title', 'Unknown Book')} ({chunk.chunk_id})"
            for chunk in source_chunks
        )

    def _fallback_answer(self, question, source_chunks):
        top_chunk = source_chunks[0]
        return (
            f"I could not reach the language model, but the most relevant context says: "
            f"{top_chunk.text}"
        )

    def _serialize_source(self, chunk):
        return {
            "citation_id": chunk.citation_id,
            "chunk_id": chunk.chunk_id,
            "text": chunk.text,
            "score": chunk.score,
            "metadata": chunk.metadata,
        }