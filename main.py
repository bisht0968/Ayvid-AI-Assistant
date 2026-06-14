from core.ollama_client import chat
from config import SYSTEM_PROMPT
from memory.memory_store import (
    init_memory,
    add_memory,
    forget_memory,
    get_all_memories,
    get_relevant_memories,
    format_memories_for_prompt,
)


def build_system_prompt(query: str = "") -> str:
    if query:
        memories = get_relevant_memories(query, top_k=3)
    else:
        memories = []
    memory_block = format_memories_for_prompt(memories)
    if memory_block:
        return f"{SYSTEM_PROMPT}\n\n{memory_block}"
    return SYSTEM_PROMPT


def handle_memory_command(user_input: str) -> str | None:
    lower = user_input.lower()

    if lower.startswith("ayvid remember "):
        fact = user_input[15:].strip()
        return add_memory(fact)

    if lower.startswith("ayvid forget "):
        fact = user_input[13:].strip()
        return forget_memory(fact)

    if lower in ["ayvid what do you remember", "ayvid what do you remember?"]:
        memories = get_all_memories()
        if not memories:
            return "I don't have anything stored in memory yet."
        lines = "\n".join(f"- {m}" for m in memories)
        return f"Here's what I remember:\n{lines}"

    return None


def run():
    print("Ayvid is ready. Type 'stop' to exit.\n")
    init_memory()

    conversation = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[Session ended]")
            break

        if not user_input:
            continue

        if user_input.lower() == "stop":
            print("[Session ended]")
            break

        memory_response = handle_memory_command(user_input)
        if memory_response:
            print(f"Ayvid: {memory_response}\n")
            continue

        # Rebuild system prompt with relevant memories for this query
        system_prompt = build_system_prompt(query=user_input)
        conversation[0] = {"role": "system", "content": system_prompt}

        conversation.append({"role": "user", "content": user_input})
        response = chat(conversation)
        conversation.append({"role": "assistant", "content": response})

        print(f"Ayvid: {response}\n")


if __name__ == "__main__":
    run()