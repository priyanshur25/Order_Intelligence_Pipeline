from src.validate import read_orders, validate_orders
from src.clients.bigquery_client import get_bigquery_client
from src.rag.agent import run_agent

# Make sure there's data to query
rows = read_orders("data/orders.csv")
valid, rejected = validate_orders(rows)
get_bigquery_client().insert_rows(valid)

questions = [
    "How much has Alice spent in total?",
    "How many orders has Bob placed?",
    "What's the weather like today?",  # should NOT trigger the tool
]

for q in questions:
    answer = run_agent(q)
    print(f"Q: {q}")
    print(f"A: {answer}\n")