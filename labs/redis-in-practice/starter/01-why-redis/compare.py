"""Chapter 1: one question, asked two ways. Run it from this folder:

    python3 compare.py

It asks Basket's slow catalogue service for the price of rice three times, then asks Redis for the same
price a thousand times, and prints how long one answer took each way. You do not need to change anything.
"""
import time

from catalogue import lookup_price, r

# The slow way: the catalogue service (1.5 s per question).
start = time.perf_counter()
for _ in range(3):
    price = lookup_price("rice")
catalogue_ms = (time.perf_counter() - start) * 1000 / 3

# The fast way: the same answer, kept in Redis.
r.set("price:rice", price)
start = time.perf_counter()
for _ in range(1000):
    r.get("price:rice")
redis_ms = (time.perf_counter() - start) * 1000 / 1000

print(f"catalogue service: {catalogue_ms:8.1f} ms per answer")
print(f"redis:             {redis_ms:8.3f} ms per answer")
print(f"Redis answered about {catalogue_ms / redis_ms:,.0f} times faster.")
