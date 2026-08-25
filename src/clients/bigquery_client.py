import json
import os
from src import config


class MockBigQueryClient:
    """Fakes BigQuery using a local JSON file as the 'table'."""

    def __init__(self, storage_path="mock_bigquery_table.json"):
        self.storage_path = storage_path
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, "w") as f:
                json.dump([], f)

    def insert_rows(self, rows):
        with open(self.storage_path) as f:
            existing = json.load(f)

        existing_ids = {r["order_id"] for r in existing}
        new_rows = [r for r in rows if r["order_id"] not in existing_ids]
        skipped = len(rows) - len(new_rows)

        existing.extend(new_rows)
        with open(self.storage_path, "w") as f:
            json.dump(existing, f, indent=2)

        print(f"[MOCK] Inserted {len(new_rows)} rows into {self.storage_path} "
              f"({skipped} skipped as duplicates)")

    def query_all(self):
        with open(self.storage_path) as f:
            return json.load(f)


class RealBigQueryClient:
    """Wraps the actual google-cloud-bigquery client."""

    def __init__(self, project_id, dataset_id="hackathon", table_id="orders"):
        from google.cloud import bigquery
        self.client = bigquery.Client(project=project_id)
        self.table_ref = f"{project_id}.{dataset_id}.{table_id}"
        self._ensure_dataset_and_table(bigquery, project_id, dataset_id, table_id)

    def _ensure_dataset_and_table(self, bigquery, project_id, dataset_id, table_id):
        dataset_ref = f"{project_id}.{dataset_id}"
        try:
            self.client.get_dataset(dataset_ref)
        except Exception:
            self.client.create_dataset(dataset_ref)
            print(f"[LIVE] Created dataset {dataset_ref}")

        schema = [
            bigquery.SchemaField("order_id", "STRING"),
            bigquery.SchemaField("customer", "STRING"),
            bigquery.SchemaField("amount", "FLOAT"),
            bigquery.SchemaField("date", "STRING"),
        ]
        try:
            self.client.get_table(self.table_ref)
        except Exception:
            table = bigquery.Table(self.table_ref, schema=schema)
            self.client.create_table(table)
            print(f"[LIVE] Created table {self.table_ref}")

    def _existing_order_ids(self):
        query = f"SELECT order_id FROM `{self.table_ref}`"
        try:
            return {row["order_id"] for row in self.client.query(query).result()}
        except Exception:
            return set()

    def insert_rows(self, rows):
        existing_ids = self._existing_order_ids()
        new_rows = [r for r in rows if r["order_id"] not in existing_ids]
        skipped = len(rows) - len(new_rows)

        if not new_rows:
            print(f"[LIVE] Nothing to insert ({skipped} duplicates skipped)")
            return

        clean_rows = [
            {
                "order_id": r["order_id"],
                "customer": r["customer"],
                "amount": float(r["amount"]),
                "date": r["date"],
            }
            for r in new_rows
        ]
        errors = self.client.insert_rows_json(self.table_ref, clean_rows)
        if errors:
            print(f"[LIVE] Insert errors: {errors}")
        else:
            print(f"[LIVE] Inserted {len(clean_rows)} rows into {self.table_ref} "
                  f"({skipped} skipped as duplicates)")

    def query_all(self):
        query = f"SELECT * FROM `{self.table_ref}`"
        return [dict(row) for row in self.client.query(query).result()]


def get_bigquery_client():
    if config.IS_LIVE:
        return RealBigQueryClient(config.GCP_PROJECT_ID)
    return MockBigQueryClient()