import json
import os

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "memory.json")


def load_memory() -> list:
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r") as f:
        content = f.read().strip()
        if not content:
            return []
        return json.loads(content)


def save_memory(memories: list):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memories, f, indent=2)


def add_memory(fact: str) -> str:
    memories = load_memory()
    fact = fact.strip()
    if fact in memories:
        return f"I already remember that."
    memories.append(fact)
    save_memory(memories)
    return f"Got it. I'll remember that."


def forget_memory(fact: str) -> str:
    memories = load_memory()
    fact = fact.strip()
    if fact in memories:
        memories.remove(fact)
        save_memory(memories)
        return f"Done. I've forgotten that."
    return f"I don't have that in my memory."


def get_all_memories() -> list:
    return load_memory()


def format_memories_for_prompt(memories: list) -> str:
    if not memories:
        return ""
    lines = "\n".join(f"- {m}" for m in memories)
    return f"Things the user has told you to remember:\n{lines}"