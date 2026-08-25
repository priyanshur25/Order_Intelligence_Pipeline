from src.validate import read_orders, validate_orders
from src.clients.bigquery_client import get_bigquery_client

rows = read_orders("data/orders.csv")
valid, rejected = validate_orders(rows)

print(f"Valid: {len(valid)}, Rejected: {len(rejected)}")

bq_client = get_bigquery_client()
bq_client.insert_rows(valid)

print("\nCurrent table contents:")
for row in bq_client.query_all():
    print(" ", row)
from src.clients.pubsub_client import get_pubsub_client

pubsub_client = get_pubsub_client()
pubsub_client.publish("pipeline-events", {
    "event": "orders_loaded",
    "valid_count": len(valid),
    "rejected_count": len(rejected),
})