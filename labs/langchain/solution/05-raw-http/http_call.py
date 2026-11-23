"""A chat model is a web API: one HTTP POST with JSON in, JSON out. No library, only httpx."""
import os

import httpx

SYSTEM = "You are Navin, the help desk assistant of the Pimpalgaon Farmers' Cooperative near Nashik. Members grow onions, grapes and tomatoes. Answer in at most three short sentences, in simple words."


def ask(question: str) -> str:
    url = os.environ["OPENAI_BASE_URL"] + "/chat/completions"
    key = os.environ["OPENAI_API_KEY"]
    body = {"model": "ai-chat",
            "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]}
    response = httpx.post(url, headers={"Authorization": f"Bearer {key}"}, json=body, timeout=60)
    response.raise_for_status()
    reply = response.json()
    return reply["choices"][0]["message"]["content"]
