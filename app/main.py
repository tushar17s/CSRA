from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from openai import OpenAIError

from app.config import ALLOWED_ORIGINS, KNOWLEDGE_BASE_DIR, STATIC_DIR
from app.models import ChatRequest, ChatResponse, DocumentUploadResponse
from app.rag import MissingApiKeyError, RagService

app = FastAPI(title="Customer Support RAG Assistant")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

rag_service = RagService()
MAX_DOCUMENT_BYTES = 1_000_000


@app.get("/")
def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/documents", response_model=DocumentUploadResponse, status_code=201)
async def add_document(file: UploadFile = File(...)) -> DocumentUploadResponse:
    filename = file.filename or ""
    if (
        not filename
        or Path(filename).name != filename
        or "/" in filename
        or "\\" in filename
    ):
        raise HTTPException(status_code=400, detail="Provide a simple document filename.")
    if Path(filename).suffix.lower() not in {".txt", ".md"}:
        raise HTTPException(
            status_code=400,
            detail="Only .txt and .md documents are supported.",
        )

    contents = await file.read(MAX_DOCUMENT_BYTES + 1)
    if len(contents) > MAX_DOCUMENT_BYTES:
        raise HTTPException(status_code=413, detail="Documents must be 1 MB or smaller.")
    try:
        text = contents.decode("utf-8")
    except UnicodeDecodeError as error:
        raise HTTPException(status_code=400, detail="Document must use UTF-8 text.") from error
    if not text.strip():
        raise HTTPException(status_code=400, detail="Document cannot be empty.")

    KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
    destination = KNOWLEDGE_BASE_DIR / filename
    if destination.exists():
        raise HTTPException(
            status_code=409,
            detail="A document with that filename already exists; choose a new name.",
        )
    destination.write_text(text, encoding="utf-8")
    return DocumentUploadResponse(
        filename=filename,
        message="Document saved. It will be embedded before the next chat request.",
    )


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        return rag_service.answer_question(request.question)
    except MissingApiKeyError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except OpenAIError as error:
        raise HTTPException(
            status_code=502,
            detail="The answer provider could not complete the request. Check the "
            "Groq API key, model name, and network connection.",
        ) from error
