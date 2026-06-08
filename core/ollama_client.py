import requests
from config import OLLAMA_BASE_URL, DEFAULT_MODEL


def chat(messages: list, model: str = DEFAULT_MODEL) -> str:
    url = f"{OLLAMA_BASE_URL}/api/chat"
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
    }
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["message"]["content"]
    except requests.exceptions.ConnectionError:
        return "[Error] Cannot reach Ollama. Is it running? Try: ollama serve"
    except requests.exceptions.Timeout:
        return "[Error] Ollama timed out. The model may be loading — try again."
    except Exception as e:
        return f"[Error] {str(e)}"