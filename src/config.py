import os
from dotenv import load_dotenv

load_dotenv()

MODE = os.getenv("MODE", "mock")  # "mock" or "live"
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

IS_LIVE = MODE == "live"