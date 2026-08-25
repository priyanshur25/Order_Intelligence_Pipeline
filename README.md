# GCP Hackathon Assessment — Order Pipeline + AI Agent

An end-to-end mock/live data pipeline that ingests order data, validates it, loads it into BigQuery, publishes a completion event via Pub/Sub, and answers natural-language questions using a Gemini-powered agent with two tools: customer order lookup and FAQ retrieval (RAG).

Every component supports two modes, controlled by a single `MODE` environment variable:
- **`mock`** (default) — runs entirely offline using local files as stand-ins for GCS, BigQuery, and Pub/Sub. No GCP credentials required.
- **`live`** — uses real Google Cloud Storage, BigQuery, and Pub/Sub, plus real Gemini API calls for embeddings, RAG, and agent responses.

## Architecture

CSV (data/orders.csv)
↓
Ingest & Validate (src/validate.py)
↓
BigQuery Load, dedupe-aware (src/clients/bigquery_client.py)
↓
Pub/Sub "pipeline complete" event (src/clients/pubsub_client.py)
↓
Interactive Q&A via Gemini Agent (src/rag/agent.py)
├── Tool: get_customer_orders → queries BigQuery
└── Tool: search_faq → RAG retrieval over FAQ documents (src/rag/)


Each cloud service (GCS, BigQuery, Pub/Sub) has a `Mock*Client` and `Real*Client` implementation behind a common interface, selected at runtime by `get_*_client()` factory functions based on `MODE`.

## Setup

1. Clone the repo and create a virtual environment:

python -m venv venv
venv\Scripts\Activate.ps1 # Windows
source venv/bin/activate # macOS/Linux

2. Install dependencies:

pip install -r requirements.txt

3. Copy `.env.example` to `.env` and fill in real values:

MODE=mock
GCP_PROJECT_ID=your-project-id
GCS_BUCKET_NAME=your-bucket-name
GEMINI_API_KEY=your-gemini-api-key

   Get a Gemini API key from https://aistudio.google.com/app/apikey.

4. (Live mode only) Authenticate:

gcloud auth application-default login


## Execution

Run the full pipeline and enter an interactive Q&A session:

python cli.py


This will:
1. Read and validate `data/orders.csv`
2. Load valid rows into BigQuery (mock or live)
3. Publish a completion event via Pub/Sub
4. Start an interactive prompt — ask about a customer's orders (e.g. "How much has Alice spent?") or company policy (e.g. "What's your return policy?"). Type `exit` to quit.

## Testing

Individual components can be tested in isolation:

python -m tests.test_storage # GCS upload/download
python -m tests.test_validate # Row validation logic
python -m tests.test_load # BigQuery load + dedupe + Pub/Sub event
python -m tests.test_llm # Basic Gemini call
python -m tests.test_rag # Document retrieval (cosine similarity)
python -m tests.test_rag_qa # Full RAG: retrieve + grounded answer
python -m tests.test_agent # Agent tool-calling (customer lookup)

All tests run in `MODE=mock` by default and require no GCP credentials. Set `MODE=live` in `.env` to test against real GCP services.

Sample data: `data/orders.csv` includes 3 valid rows and 3 intentionally invalid rows (missing customer, negative amount, malformed date) to exercise validation logic.

## Assumptions

- Order data arrives as a single CSV with columns: `order_id, customer, amount, date` (format `YYYY-MM-DD`).
- Customer names are matched case-insensitively; no handling for typos or fuzzy matching.
- `order_id` is treated as the unique key for deduplication on load.
- The FAQ document set is small (5 entries) and hardcoded for demonstration; a production system would load these from a managed source.

## Known limitations

- **Mock embeddings** (`MockEmbeddingClient`) use word-hash overlap rather than true semantic similarity, and can retrieve an incorrect FAQ document when a question shares few literal words with the correct entry (verified: this is resolved when using real Gemini embeddings in live mode).
- **No mock for the LLM/agent layer** — `run_agent()` and the RAG generation step always call the real Gemini API, even in `MODE=mock`. Only the data-layer clients (GCS, BigQuery, Pub/Sub) have full mock implementations.
- Pub/Sub events are published but not consumed by any subscriber in this project — there's no downstream service reacting to the "pipeline complete" event yet.
- Validation does not check for duplicate `order_id`s within a single CSV batch, only against rows already loaded.
- Composer/Airflow-style orchestration was not implemented; `cli.py`'s `run_pipeline()` function represents what would become an Airflow DAG in a production setup.

## Security considerations

- All secrets (Gemini API key, project ID, bucket name) are read from a local `.env` file, which is excluded from version control via `.gitignore`.
- `.env.example` provides placeholder values so the repo is runnable by others without exposing real credentials.
- No credentials are hardcoded anywhere in source files.
- Live-mode GCP authentication uses Application Default Credentials (`gcloud auth application-default login`) rather than downloaded service account key files, avoiding long-lived credential files on disk.
- Only mock/synthetic data (`data/orders.csv`) is used; no real customer or personally identifiable information is included in this repository.

## AI-tool usage

This project was built with the assistance of Claude (Anthropic), used for:
- Explaining GCP concepts (BigQuery datasets/tables, Pub/Sub topics, embeddings, cosine similarity) at each implementation step
- Debugging Python dependency conflicts during environment setup
- Reviewing and improving the mock/live client pattern and BigQuery dedupe logic
- Verifying current Gemini API model/SDK names against live documentation, since some model names referenced in older tutorials had been deprecated
All architectural decisions, code review, and testing were performed interactively with each step run and verified before proceeding to the next.