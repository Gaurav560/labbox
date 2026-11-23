"""The same call through the official OpenAI Python SDK: typed objects, retries and timeouts built in."""
import os

from openai import OpenAI

SYSTEM = "You are Navin, the help desk assistant of the Pimpalgaon Farmers' Cooperative near Nashik. Members grow onions, grapes and tomatoes. Answer in at most three short sentences, in simple words."


def client() -> OpenAI:
    # TODO (task sdk_client): return OpenAI(...) with base_url and api_key from the environment
    #   (OPENAI_BASE_URL, OPENAI_API_KEY), timeout=60 and max_retries=2.
    return None


def ask(openai: OpenAI, question: str):
    """Returns the answer text and the token usage object."""
    # TODO (task sdk_ask): call openai.chat.completions.create(model="ai-chat", messages=[...]) with the system message
    #   and the question, and return (the first choice's message content, completion.usage).
    return "", None
