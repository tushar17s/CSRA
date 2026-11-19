import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.rag import MissingApiKeyError


class ApiRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health_route_returns_ok(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_document_upload_saves_supported_text(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            with patch("app.main.KNOWLEDGE_BASE_DIR", Path(temporary_directory)):
                response = self.client.post(
                    "/documents",
                    files={"file": ("new_article.md", b"# New article\nExample text.")},
                )
                saved_document = Path(temporary_directory) / "new_article.md"

                self.assertEqual(response.status_code, 201)
                self.assertTrue(saved_document.exists())
                self.assertIn("next chat request", response.json()["message"])

    def test_document_upload_rejects_unsupported_extension(self) -> None:
        response = self.client.post(
            "/documents",
            files={"file": ("article.pdf", b"not a text article")},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(".txt and .md", response.json()["detail"])

    def test_chat_reports_a_missing_provider_key(self) -> None:
        with patch(
            "app.main.rag_service.answer_question",
            side_effect=MissingApiKeyError("Set GROQ_API_KEY in .env."),
        ):
            response = self.client.post("/chat", json={"question": "Hello"})

        self.assertEqual(response.status_code, 503)
        self.assertIn("GROQ_API_KEY", response.json()["detail"])

    def test_chat_rejects_a_blank_question(self) -> None:
        response = self.client.post("/chat", json={"question": "   "})

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
