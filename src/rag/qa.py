from src.rag.retriever import Retriever
from src.clients.llm_client import ask

PROMPT_TEMPLATE = """Answer the question using ONLY the context below. \
If the context doesn't contain the answer, say you don't have that information.

Context:
{context}

Question: {question}

Answer:"""


class RagQA:
    def __init__(self):
        self.retriever = Retriever()

    def answer(self, question: str) -> str:
        context = self.retriever.retrieve(question, top_k=1)[0]
        prompt = PROMPT_TEMPLATE.format(context=context, question=question)
        return ask(prompt)