from src.validate import read_orders, validate_orders
from src.clients.bigquery_client import get_bigquery_client
from src.clients.pubsub_client import get_pubsub_client
from src.rag.agent import run_agent


def run_pipeline():
    print("=== Running pipeline ===")
    rows = read_orders("data/orders.csv")
    valid, rejected = validate_orders(rows)
    print(f"Valid: {len(valid)}, Rejected: {len(rejected)}")

    if rejected:
        print("Rejected rows:")
        for r in rejected:
            print(f"  order_id={r['order_id']}: {r['_errors']}")

    bq_client = get_bigquery_client()
    bq_client.insert_rows(valid)

    pubsub_client = get_pubsub_client()
    pubsub_client.publish("pipeline-events", {
        "event": "orders_loaded",
        "valid_count": len(valid),
        "rejected_count": len(rejected),
    })
    print("=== Pipeline complete ===\n")


def run_qa_loop():
    print("Ask a question about orders or company policy (type 'exit' to quit):")
    while True:
        question = input("> ")
        if question.strip().lower() in ("exit", "quit"):
            break
        answer = run_agent(question)
        print(answer, "\n")


if __name__ == "__main__":
    run_pipeline()
    run_qa_loop()