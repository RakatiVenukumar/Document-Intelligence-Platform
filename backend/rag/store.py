from pathlib import Path
from django.conf import settings


class ChromaVectorStore:
    """Persist and query vector data in a local ChromaDB collection."""

    def __init__(self, collection_name="book_chunks", persist_directory=None):
        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory or settings.BASE_DIR / "chroma_store")
        self._client = None

    def _get_client(self):
        if self._client is None:
            import chromadb

            self._client = chromadb.PersistentClient(path=str(self.persist_directory))

        return self._client

    def get_collection(self):
        return self._get_client().get_or_create_collection(
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

    def query(self, query_embeddings, n_results=5, where=None):
        collection = self.get_collection()
        query_kwargs = {
            "query_embeddings": query_embeddings,
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }
        if where is not None:
            query_kwargs["where"] = where

        return collection.query(**query_kwargs)