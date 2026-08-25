from src.clients.bigquery_client import get_bigquery_client


def get_customer_orders(customer_name: str) -> str:
    """Looks up all orders placed by a specific customer and returns their total spend.

    Args:
        customer_name: The name of the customer to look up, e.g. "Alice".
    """
    bq_client = get_bigquery_client()
    all_rows = bq_client.query_all()

    customer_rows = [r for r in all_rows if r["customer"].lower() == customer_name.lower()]

    if not customer_rows:
        return f"No orders found for customer '{customer_name}'."

    total = sum(float(r["amount"]) for r in customer_rows)
    order_count = len(customer_rows)
    return f"{customer_name} has placed {order_count} order(s) totaling ${total:.2f}."

from src.rag.retriever import Retriever

_retriever = None


def _get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever


def search_faq(query: str) -> str:
    """Searches company FAQ documents (returns, shipping, payments, password
    reset, order cancellation) and returns the most relevant one.

    Args:
        query: The customer's question to search the FAQ for.
    """
    retriever = _get_retriever()
    result = retriever.retrieve(query, top_k=1)
    return result[0]
from google import genai
from google.genai import types
from src import config


def run_agent(question: str) -> str:
    client = genai.Client(api_key=config.GEMINI_API_KEY)

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=question,
        config=types.GenerateContentConfig(
            tools=[get_customer_orders, search_faq],
        ),
    )
    return response.text