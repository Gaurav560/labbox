"""A chat model is a web API: one HTTP POST with JSON in, JSON out. No library, only httpx."""
import os

import httpx

SYSTEM = "You are Navin, the help desk assistant of the Pimpalgaon Farmers' Cooperative near Nashik. Members grow onions, grapes and tomatoes. Answer in at most three short sentences, in simple words."


def ask(question: str) -> str:
    url = os.environ["OPENAI_BASE_URL"] + "/chat/completions"
    key = os.environ["OPENAI_API_KEY"]
    # TODO (task send_request): POST to url, with the header Authorization: Bearer <key>, and a JSON body with
    #   "model": "ai-chat" and "messages": the system message (role "system", content SYSTEM), then the question
    #   (role "user"). Use httpx.post(url, headers=..., json=..., timeout=60).
    reply = {}
    # TODO (task read_answer): the reply's JSON has the answer at choices[0].message.content: return that text.
    return ""
