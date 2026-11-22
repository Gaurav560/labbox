"""Chapter 11: thirty customers tap the same delivery slot at the same moment.

    python3 book_race.py

Your app must be running on port 8000. A correct app tells exactly one customer the slot is theirs.
"""
from concurrent.futures import ThreadPoolExecutor
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import redis

r = redis.Redis(host="redis", decode_responses=True)
r.delete("booking:slot:1800")


def book(i):
    try:
        return urlopen(Request(f"http://localhost:8000/book/1800?customer=c{i}", method="POST")).status
    except HTTPError as e:
        return e.code


with ThreadPoolExecutor(max_workers=30) as pool:
    codes = list(pool.map(book, range(30)))
print(f"told the slot is theirs: {codes.count(200)}, told no: {codes.count(409)}")
print(f"the slot is stored for: {r.get('booking:slot:1800')}")
