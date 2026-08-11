import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in .env")

if not MODEL:
    raise ValueError("GEMINI_MODEL is not set in .env")

client = genai.Client(api_key=API_KEY)


def generate_plan(prompt: str) -> str:
    """
    Send a prompt to Gemini and return the generated response.
    This function is used by the agent's Plan stage.
    """

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response")

    return response.text.strip()