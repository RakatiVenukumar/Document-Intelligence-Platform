from pathlib import Path

import chromadb
from django.conf import settings


class ChromaVectorStore:
    """Persist and query vector data in a local ChromaDB collection."""

    def __init__(self, collection_name="book_chunks", persist_directory=None):
        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory or settings.BASE_DIR / "chroma_store")
        self.client = chromadb.PersistentClient(path=str(self.persist_directory))

    def get_collection(self):
        return self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_chunks(self, ids, documents, embeddings, metadatas):
        collection = self.get_collection()
        collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        return collection