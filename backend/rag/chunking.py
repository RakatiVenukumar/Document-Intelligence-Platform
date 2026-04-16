from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class TextChunk:
    index: int
    text: str
    start_word: int
    end_word: int


class TextChunker:
    """Split text into overlapping word chunks for RAG indexing."""

    def __init__(self, chunk_size=300, overlap=50):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")
        if overlap < 0:
            raise ValueError("overlap cannot be negative")
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text):
        words = text.split()
        if not words:
            return []

        chunks = []
        start = 0
        index = 0

        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk_words = words[start:end]

            chunks.append(
                TextChunk(
                    index=index,
                    text=" ".join(chunk_words),
                    start_word=start,
                    end_word=end,
                )
            )

            if end >= len(words):
                break

            start = end - self.overlap
            index += 1

        return chunks