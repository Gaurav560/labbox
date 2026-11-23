"""The same call through the official OpenAI Python SDK: typed objects, retries and timeouts built in."""
import os

from openai import OpenAI

SYSTEM = "You are Navin, the help desk assistant of the Pimpalgaon Farmers' Cooperative near Nashik. Members grow onions, grapes and tomatoes. Answer in at most three short sentences, in simple words."


def client() -> OpenAI:
    return OpenAI(base_url=os.environ["OPENAI_BASE_URL"], api_key=os.environ["OPENAI_API_KEY"],
                  timeout=60, max_retries=2)


def ask(openai: OpenAI, question: str):
    """Returns the answer text and the token usage object."""
    completion = openai.chat.completions.create(
        model="ai-chat",
        messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}],
    )
    return completion.choices[0].message.content, completion.usage
