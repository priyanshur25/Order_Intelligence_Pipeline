from src.clients.storage_client import get_storage_client

client = get_storage_client()
client.upload_file("data/orders.csv", "orders.csv")
client.download_file("orders.csv", "data/orders_downloaded.csv")