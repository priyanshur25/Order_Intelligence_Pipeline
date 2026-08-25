import hashlib
import math
from src import config


STOP_WORDS = {
    "a", "an", "the", "is", "are", "do", "does", "to", "for", "of", "in",
    "on", "i", "you", "your", "my", "how", "what", "get", "have", "has",
    "if", "into", "with", "and", "or", "can", "go",
}


def _mock_embed_one(text: str, dims: int = 64) -> list[float]:
    """Deterministic fake embedding: hashes meaningful words into a fixed-size
    vector, skipping common stop words so they don't drown out real content
    words. Still not true semantic understanding, but good enough to prove
    the retrieval pipeline end-to-end without any API calls."""
    vector = [0.0] * dims
    words = [w.strip(".,'?") for w in text.lower().split()]
    words = [w for w in words if w and w not in STOP_WORDS]
    for word in words:
        h = int(hashlib.md5(word.encode()).hexdigest(), 16)
        index = h % dims
        vector[index] += 1.0
    return vector


class MockEmbeddingClient:
    def embed(self, texts: list[str]) -> list[list[float]]:
        return [_mock_embed_one(t) for t in texts]


class RealEmbeddingClient:
    def __init__(self):
        from google import genai
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)

    def embed(self, texts: list[str]) -> list[list[float]]:
        result = self.client.models.embed_content(
            model="gemini-embedding-001",
            contents=texts,
        )
        return [e.values for e in result.embeddings]


def get_embedding_client():
    if config.IS_LIVE:
        return RealEmbeddingClient()
    return MockEmbeddingClient()