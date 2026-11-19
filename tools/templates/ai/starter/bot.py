"""A tiny assistant. Run it for real (it talks to the lab's model):  python bot.py "your question"
The check calls ask() with a fake client, so it can see exactly what you send."""
import sys

SYSTEM = "You are a helpful barista. Answer in one short sentence."


def ask(client, question: str) -> str:
    # TODO(ask): send SYSTEM and the question to the model lab-chat, return the reply text.
    return ""


if __name__ == "__main__":
    from openai import OpenAI

    print(ask(OpenAI(), " ".join(sys.argv[1:]) or "What is a flat white?"))
