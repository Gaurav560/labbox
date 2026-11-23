"""Chapter 16: run with  python main.py"""
import time

from streaming import answer_text, navin_agent, steps

agent = navin_agent()
question = "What would 30 crates of tomatoes cost to store for 6 days, and what is the tomato rate?"
start = time.perf_counter()
steps(agent, question, lambda line: print(f"{time.perf_counter() - start:5.2f}s  {line}"))

print()
start = time.perf_counter()
text = answer_text(agent, question, lambda piece: print(piece, end="", flush=True))
print(f"\n\n{len(text)} characters in {time.perf_counter() - start:.2f}s")
