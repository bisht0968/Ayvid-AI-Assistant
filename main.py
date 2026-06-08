from core.ollama_client import chat
from config import SYSTEM_PROMPT

def run():
    print("Ayvid is ready. Type 'stop' to exit.\n")

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

        conversation.append({"role": "user", "content": user_input})
        response = chat(conversation)
        conversation.append({"role": "assistant", "content": response})

        print(f"Ayvid: {response}\n")

if __name__ == "__main__":
    run()