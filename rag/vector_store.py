import chromadb
import os

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "chroma")

_client = None
_memory_collection = None
_document_collection = None


def get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_PATH)
    return _client


def get_memory_collection():
    global _memory_collection
    if _memory_collection is None:
        _memory_collection = get_client().get_or_create_collection(
            name="memories",
            metadata={"hnsw:space": "cosine"}
        )
    return _memory_collection


def get_document_collection():
    global _document_collection
    if _document_collection is None:
        _document_collection = get_client().get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
    return _document_collection


# --- Memory operations ---

def add_to_vector_store(fact: str, embedding: list, fact_id: str):
    get_memory_collection().add(
        ids=[fact_id],
        embeddings=[embedding],
        documents=[fact]
    )


def query_vector_store(embedding: list, top_k: int = 3) -> list:
    collection = get_memory_collection()
    count = collection.count()
    if count == 0:
        return []
    results = collection.query(
        query_embeddings=[embedding],
        n_results=min(top_k, count)
    )
    return results["documents"][0] if results["documents"] else []


def delete_from_vector_store(fact_id: str):
    get_memory_collection().delete(ids=[fact_id])


def get_all_from_vector_store() -> list:
    collection = get_memory_collection()
    if collection.count() == 0:
        return []
    return collection.get()["documents"]


# --- Document operations ---

def add_document_chunk(chunk: str, embedding: list, chunk_id: str, source: str):
    get_document_collection().add(
        ids=[chunk_id],
        embeddings=[embedding],
        documents=[chunk],
        metadatas=[{"source": source}]
    )


def query_document_store(embedding: list, top_k: int = 3) -> list:
    collection = get_document_collection()
    count = collection.count()
    if count == 0:
        return []
    results = collection.query(
        query_embeddings=[embedding],
        n_results=min(top_k, count)
    )
    docs = results["documents"][0] if results["documents"] else []
    sources = [m["source"] for m in results["metadatas"][0]] if results["metadatas"] else []
    return list(zip(docs, sources))


def get_all_document_sources() -> list:
    collection = get_document_collection()
    if collection.count() == 0:
        return []
    results = collection.get(include=["metadatas"])
    return [m["source"] for m in results["metadatas"]]