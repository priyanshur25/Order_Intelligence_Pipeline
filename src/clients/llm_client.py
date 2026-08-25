from google import genai
from src import config


def get_llm_client():
    return genai.Client(api_key=config.GEMINI_API_KEY)


def ask(prompt: str, model: str = "gemini-3.6-flash") -> str:
    client = get_llm_client()
    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )
    return response.text