"""Chapter 8: run with  python main.py"""
import time

from params import steady_model, stream_answer

model = steady_model()
start = time.perf_counter()
first = []


def show(piece: str) -> None:
    if not first and piece:
        first.append(time.perf_counter() - start)
    print(f"[{piece}]", end="", flush=True)


text = stream_answer(model, "Why do onion prices rise in the monsoon?", show)
print(f"\n\nfirst piece after {first[0] * 1000:.0f} ms, all {len(text)} characters after {(time.perf_counter() - start) * 1000:.0f} ms")
