from dataclasses import dataclass
import hashlib
import json
from typing import Dict, List, Optional

from django.core.cache import cache

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
        cache_key = self._cache_key(question, book_id, top_k)
        cached_response = cache.get(cache_key)
        if cached_response is not None:
            return cached_response

        retrieved_chunks = self.retriever.search(question=question, book_id=book_id, top_k=top_k)
        source_chunks = self._number_sources(retrieved_chunks)

        if not source_chunks:
            response = {
                "answer": "No relevant book context was found for this question.",
                "source_chunks": [],
                "used_llm": False,
            }
            cache.set(cache_key, response, timeout=3600)
            return response

        context = self._build_context(source_chunks)
        citations = self._build_citations(source_chunks)
        llm_error = None

        try:
            answer = self.llm_client.generate(question=question, context=context, citations=citations)
            used_llm = True
        except Exception as exc:
            answer = self._fallback_answer(question, source_chunks)
            used_llm = False
            llm_error = f"{type(exc).__name__}: {exc}"

        response = {
            "answer": answer,
            "source_chunks": [self._serialize_source(chunk) for chunk in source_chunks],
            "used_llm": used_llm,
        }
        if llm_error is not None:
            response["llm_error"] = llm_error
        if used_llm:
            cache.set(cache_key, response, timeout=3600)
        return response

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

    def _cache_key(self, question, book_id, top_k):
        llm_provider = getattr(self.llm_client, "provider", "unknown")
        llm_model = getattr(self.llm_client, "model", "unknown")
        fingerprint = json.dumps(
            {
                "question": question,
                "book_id": book_id,
                "top_k": top_k,
                "llm_provider": llm_provider,
                "llm_model": llm_model,
            },
            sort_keys=True,
        )
        digest = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()
        return f"rag-answer:{digest}"