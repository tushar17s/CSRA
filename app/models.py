from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)

    @field_validator("question")
    @classmethod
    def question_must_contain_text(cls, value: str) -> str:
        question = value.strip()
        if not question:
            raise ValueError("Question cannot be blank.")
        return question


class RetrievedPassage(BaseModel):
    source: str
    text: str
    similarity: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    passages: list[RetrievedPassage]


class DocumentUploadResponse(BaseModel):
    filename: str
    message: str
