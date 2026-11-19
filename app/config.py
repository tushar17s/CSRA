import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"
VECTOR_STORE_PATH = PROJECT_ROOT / "data" / "vector_store.json"
STATIC_DIR = PROJECT_ROOT / "static"

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]
