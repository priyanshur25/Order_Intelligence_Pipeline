import math
from src.rag.documents import DOCUMENTS
from src.clients.embedding_client import get_embedding_client


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    magnitude_a = math.sqrt(sum(a * a for a in vec_a))
    magnitude_b = math.sqrt(sum(b * b for b in vec_b))
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    return dot_product / (magnitude_a * magnitude_b)


class Retriever:
    def __init__(self):
        self.embedding_client = get_embedding_client()
        self.documents = DOCUMENTS
        self.doc_embeddings = self.embedding_client.embed(self.documents)

    def retrieve(self, query: str, top_k: int = 1) -> list[str]:
        query_embedding = self.embedding_client.embed([query])[0]

        scored = []
        for doc, doc_embedding in zip(self.documents, self.doc_embeddings):
            score = cosine_similarity(query_embedding, doc_embedding)
            scored.append((score, doc))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [doc for score, doc in scored[:top_k]]