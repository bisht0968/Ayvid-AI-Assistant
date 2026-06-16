import getpass
from core.ollama_client import chat
from config import SYSTEM_PROMPT, ACCESS_PIN, WEB_TRIGGER_KEYWORDS
from memory.memory_store import (
    init_memory,
    add_memory,
    forget_memory,
    get_all_memories,
    get_relevant_memories,
)
from documents.ingestion import ingest_document, list_documents
from rag.vector_store import query_document_store
from rag.embedder import embed
from web.search import search_web
from web.scraper import get_web_context


def verify_pin() -> bool:
    attempts = 3
    while attempts > 0:
        pin = getpass.getpass("Enter PIN: ")
        if pin == ACCESS_PIN:
            return True
        attempts -= 1
        if attempts > 0:
            print(f"Wrong PIN. {attempts} attempt{'s' if attempts > 1 else ''} left.")
        else:
            print("Access denied.")
    return False


def needs_web_search(query: str) -> bool:
    lower = query.lower()
    return any(keyword in lower for keyword in WEB_TRIGGER_KEYWORDS)


def get_relevant_doc_context(query: str) -> list:
    query_embedding = embed(query)
    return query_document_store(query_embedding, top_k=3)


def build_system_prompt(query: str = "", web_context: list = None) -> str:
    prompt = SYSTEM_PROMPT

    if query:
        # Inject relevant memories
        memories = get_relevant_memories(query, top_k=3)
        if memories:
            lines = "\n".join(f"- {m}" for m in memories)
            prompt += f"\n\nRelevant things the user has told you to remember:\n{lines}"

        # Inject relevant document chunks
        doc_results = get_relevant_doc_context(query)
        if doc_results:
            prompt += "\n\nRelevant context from the user's documents:"
            for chunk, source in doc_results:
                prompt += f"\n\n[From: {source}]\n{chunk}"
            prompt += "\n\nMention the source file name when using document context."

    # Inject web context
    if web_context:
        prompt += "\n\nCurrent web search results for this query:"
        for item in web_context:
            prompt += f"\n\n[Source: {item['title']} — {item['url']}]\n{item['content']}"
        prompt += "\n\nUse this web context to answer. Label your response with 'Likely —' and cite the source URLs."

    return prompt


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
            return "Nothing stored yet bro."
        lines = "\n".join(f"- {m}" for m in memories)
        return f"Here's what I've got:\n{lines}"

    return None


def handle_document_command(user_input: str) -> str | None:
    lower = user_input.lower()

    if lower.startswith("ayvid load document "):
        filename = user_input[20:].strip()
        return ingest_document(filename)

    if lower in ["ayvid what documents do you have", "ayvid what documents do you have?"]:
        docs = list_documents()
        if not docs:
            return "No documents loaded yet. Drop a file in user_docs/ and tell me to load it."
        lines = "\n".join(f"- {d}" for d in docs)
        return f"Documents I have loaded:\n{lines}"

    return None


def run():
    if not verify_pin():
        return

    print("\nAyvid is ready. Type 'stop' to exit.\n")
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

        doc_response = handle_document_command(user_input)
        if doc_response:
            print(f"Ayvid: {doc_response}\n")
            continue

        # Web search if needed
        web_context = None
        if needs_web_search(user_input):
            print("Ayvid: Searching the web...\n")
            results = search_web(user_input)
            if results:
                web_context = get_web_context(results)

        system_prompt = build_system_prompt(query=user_input, web_context=web_context)
        conversation[0] = {"role": "system", "content": system_prompt}

        conversation.append({"role": "user", "content": user_input})
        response = chat(conversation)
        conversation.append({"role": "assistant", "content": response})

        print(f"Ayvid: {response}\n")


if __name__ == "__main__":
    run()