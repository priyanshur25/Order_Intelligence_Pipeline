from src.rag.qa import RagQA

qa = RagQA()

questions = [
    "How long do I have to return something?",
    "What payment methods do you accept?",
]

for q in questions:
    answer = qa.answer(q)
    print(f"Q: {q}")
    print(f"A: {answer}\n")