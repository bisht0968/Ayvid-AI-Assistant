import json
import os
import uuid
from rag.embedder import embed
from rag.vector_store import (
    add_to_vector_store,
    delete_from_vector_store,
    get_all_from_vector_store,
    query_vector_store,
)

# Legacy JSON path — used only for migration
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "memory.json")


def _migrate_json_to_chroma():
    if not os.path.exists(MEMORY_FILE):
        return
    with open(MEMORY_FILE, "r") as f:
        content = f.read().strip()
    if not content:
        return
    facts = json.loads(content)
    if not facts:
        return
    print(f"[Migrating {len(facts)} memories from JSON to ChromaDB...]")
    for fact in facts:
        fact_id = str(uuid.uuid4())
        embedding = embed(fact)
        add_to_vector_store(fact, embedding, fact_id)
    os.rename(MEMORY_FILE, MEMORY_FILE + ".migrated")
    print("[Migration complete]")


def init_memory():
    _migrate_json_to_chroma()


def add_memory(fact: str) -> str:
    fact = fact.strip()
    existing = get_all_from_vector_store()
    if fact in existing:
        return "I already remember that."
    fact_id = str(uuid.uuid4())
    embedding = embed(fact)
    add_to_vector_store(fact, embedding, fact_id)
    return "Got it. I'll remember that."


def forget_memory(fact: str) -> str:
    fact = fact.strip()
    collection_results = get_all_from_vector_store()
    if fact not in collection_results:
        return "I don't have that in my memory."
    # Find the ID for this fact
    from rag.vector_store import get_collection
    collection = get_collection()
    results = collection.get()
    for doc, doc_id in zip(results["documents"], results["ids"]):
        if doc == fact:
            delete_from_vector_store(doc_id)
            return "Done. I've forgotten that."
    return "I don't have that in my memory."


def get_all_memories() -> list:
    return get_all_from_vector_store()


def get_relevant_memories(query: str, top_k: int = 3) -> list:
    query_embedding = embed(query)
    return query_vector_store(query_embedding, top_k=top_k)


def format_memories_for_prompt(memories: list) -> str:
    if not memories:
        return ""
    lines = "\n".join(f"- {m}" for m in memories)
    return f"Relevant things the user has told you to remember:\n{lines}"