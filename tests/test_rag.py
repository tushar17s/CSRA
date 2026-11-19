import unittest

from app.rag import (
    KnowledgeChunk,
    FALLBACK_ANSWER,
    RagService,
    ScoredChunk,
    chunk_text,
    cosine_similarity,
    select_relevant_passages,
)


class ChunkTextTests(unittest.TestCase):
    def test_chunks_overlap_and_cover_the_input(self) -> None:
        text = "abcdefghij"
        chunks = chunk_text(text, chunk_size=6, overlap=2)

        self.assertEqual(chunks, ["abcdef", "efghij"])

    def test_empty_text_returns_no_chunks(self) -> None:
        self.assertEqual(chunk_text(" \n "), [])

    def test_invalid_overlap_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            chunk_text("text", chunk_size=4, overlap=4)


class RetrievalHelperTests(unittest.TestCase):
    def test_cosine_similarity_handles_direction_and_zero_vectors(self) -> None:
        self.assertAlmostEqual(cosine_similarity([1, 0], [2, 0]), 1.0)
        self.assertEqual(cosine_similarity([0, 0], [1, 0]), 0.0)

    def test_low_scoring_passages_are_not_returned(self) -> None:
        weak_match = ScoredChunk(
            KnowledgeChunk("shipping.md", "Shipping details", [1.0]),
            similarity=0.6,
        )
        strong_match = ScoredChunk(
            KnowledgeChunk("returns.md", "Return details", [0.8]),
            similarity=0.8,
        )

        selected = select_relevant_passages(
            [weak_match, strong_match],
            threshold=0.68,
            limit=3,
        )

        self.assertEqual([item.chunk.source for item in selected], ["returns.md"])

    def test_no_retrieved_passages_returns_fallback_without_generation(self) -> None:
        service = RagService()
        service.retrieve = lambda question: []

        result = service.answer_question("Is weekend phone support available?")

        self.assertEqual(result["answer"], FALLBACK_ANSWER)
        self.assertEqual(result["sources"], [])
        self.assertEqual(result["passages"], [])


if __name__ == "__main__":
    unittest.main()
