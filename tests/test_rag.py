from src.rag.retriever import Retriever

retriever = Retriever()

questions = [
    "How long do I have to return something?",
    "What payment methods do you accept?",
    "How do I get into my account if I forgot my password?",
]

for q in questions:
    result = retriever.retrieve(q, top_k=1)
    print(f"Q: {q}")
    print(f"Retrieved: {result[0]}\n")