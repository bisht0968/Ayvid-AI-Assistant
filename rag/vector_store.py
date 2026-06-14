import chromadb
import os

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "chroma")

_client = None
_collection = None


def get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = _client.get_or_create_collection(
            name="memories",
            metadata={"hnsw:space": "cosine"}
        )
    return _collection


def add_to_vector_store(fact: str, embedding: list, fact_id: str):
    collection = get_collection()
    collection.add(
        ids=[fact_id],
        embeddings=[embedding],
        documents=[fact]
    )


def query_vector_store(embedding: list, top_k: int = 3) -> list:
    collection = get_collection()
    count = collection.count()
    if count == 0:
        return []
    results = collection.query(
        query_embeddings=[embedding],
        n_results=min(top_k, count)
    )
    return results["documents"][0] if results["documents"] else []


def delete_from_vector_store(fact_id: str):
    collection = get_collection()
    collection.delete(ids=[fact_id])


def get_all_from_vector_store() -> list:
    collection = get_collection()
    if collection.count() == 0:
        return []
    results = collection.get()
    return results["documents"]