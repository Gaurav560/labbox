"""Chapter 9: run with  python main.py"""
from honest import answer_cost, ask

for question in ["What is today's onion rate?", "What is today's garlic rate?", "Can I harvest grapes 4 days after spraying?"]:
    reply = ask(question)
    usage = reply.usage_metadata
    print(f"> {question}\n{reply.content}")
    print(f"  ({usage['input_tokens']} in, {usage['output_tokens']} out, ${answer_cost(reply):.6f})\n")
