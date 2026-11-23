"""A tiny assistant. Run it for real (it talks to the lab's model):  python bot.py "your question"
The check calls ask() with a fake client, so it can see exactly what you send."""
import sys

SYSTEM = "You are a helpful bookshop assistant. Answer in one short sentence."


def ask(client, question: str) -> str:
    response = client.chat.completions.create(
        model="lab-chat",
        messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    from openai import OpenAI

    print(ask(OpenAI(), " ".join(sys.argv[1:]) or "What is a first edition?"))
