"""Chapter 6: run with  python main.py"""
from sdk import ask, client

answer, usage = ask(client(), "Do you store tomatoes in cold storage?")
print(answer)
print(f"\n{usage.prompt_tokens} tokens in, {usage.completion_tokens} tokens out")
