import os
import shutil
from src import config


class MockStorageClient:
    """Fakes GCS using a local folder. Same interface as the real client."""

    def __init__(self, local_root="mock_gcs_bucket"):
        self.local_root = local_root
        os.makedirs(self.local_root, exist_ok=True)

    def upload_file(self, local_path, remote_name):
        dest = os.path.join(self.local_root, remote_name)
        shutil.copy(local_path, dest)
        print(f"[MOCK] Uploaded {local_path} -> {dest}")
        return dest

    def download_file(self, remote_name, local_path):
        src = os.path.join(self.local_root, remote_name)
        shutil.copy(src, local_path)
        print(f"[MOCK] Downloaded {src} -> {local_path}")
        return local_path


class RealStorageClient:
    """Wraps the actual google-cloud-storage client."""

    def __init__(self, bucket_name):
        from google.cloud import storage
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    def upload_file(self, local_path, remote_name):
        blob = self.bucket.blob(remote_name)
        blob.upload_from_filename(local_path)
        print(f"[LIVE] Uploaded {local_path} -> gs://{self.bucket.name}/{remote_name}")
        return f"gs://{self.bucket.name}/{remote_name}"

    def download_file(self, remote_name, local_path):
        blob = self.bucket.blob(remote_name)
        blob.download_to_filename(local_path)
        print(f"[LIVE] Downloaded gs://{self.bucket.name}/{remote_name} -> {local_path}")
        return local_path


def get_storage_client():
    if config.IS_LIVE:
        return RealStorageClient(config.GCS_BUCKET_NAME)
    return MockStorageClient()