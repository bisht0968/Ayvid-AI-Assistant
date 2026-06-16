import os
import uuid
from rag.embedder import embed
from rag.vector_store import add_document_chunk, get_all_document_sources

USER_DOCS_PATH = os.path.join(os.path.dirname(__file__), "user_docs")

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def chunk_text(text: str) -> list:
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def read_txt(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def read_pdf(filepath: str) -> str:
    from pypdf import PdfReader
    reader = PdfReader(filepath)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def read_md(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def ingest_document(filename: str) -> str:
    filepath = os.path.join(USER_DOCS_PATH, filename)

    if not os.path.exists(filepath):
        return f"File '{filename}' not found in user_docs/."

    existing = get_all_document_sources()
    if filename in existing:
        return f"'{filename}' is already loaded. I have it."

    ext = os.path.splitext(filename)[1].lower()

    if ext == ".txt":
        text = read_txt(filepath)
    elif ext == ".pdf":
        text = read_pdf(filepath)
    elif ext in [".md", ".markdown"]:
        text = read_md(filepath)
    else:
        return f"Sorry, I can only read .txt, .pdf, and .md files right now."

    if not text.strip():
        return f"'{filename}' appears to be empty or unreadable."

    chunks = chunk_text(text)
    for chunk in chunks:
        chunk_id = str(uuid.uuid4())
        embedding = embed(chunk)
        add_document_chunk(chunk, embedding, chunk_id, filename)

    return f"Done. Loaded '{filename}' — {len(chunks)} chunks stored."


def list_documents() -> list:
    return list(set(get_all_document_sources()))