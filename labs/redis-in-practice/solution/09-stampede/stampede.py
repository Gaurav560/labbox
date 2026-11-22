"""Chapter 9: a sale starts, and 30 customers open the same item at the same moment.

    python3 stampede.py paneer

It empties the cache for that item, sends 30 requests to your app at once, and counts how many of them
reached the slow catalogue service. Your app must be running on port 8000.
"""
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen

from catalogue import r

item = sys.argv[1] if len(sys.argv) > 1 else "paneer"
r.delete(f"price:{item}")
before = int(r.get("catalogue:calls") or 0)

start = time.perf_counter()
with ThreadPoolExecutor(max_workers=30) as pool:
    answers = list(pool.map(lambda _: urlopen(f"http://localhost:8000/price/{item}").status, range(30)))
seconds = time.perf_counter() - start

calls = int(r.get("catalogue:calls") or 0) - before
print(f"30 requests for {item}: {answers.count(200)} answered in {seconds:.1f} s")
print(f"catalogue calls: {calls}")
