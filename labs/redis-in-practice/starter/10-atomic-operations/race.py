"""Chapter 10: twenty redemptions of 100 coins arrive at the same moment, and Asha has only 500 coins.

    python3 race.py

Your app must be running on port 8000. A correct app lets exactly 5 through and never goes below zero.
"""
from concurrent.futures import ThreadPoolExecutor
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import redis

r = redis.Redis(host="redis", decode_responses=True)
r.set("coins:42", 500)


def spend(_):
    try:
        return urlopen(Request("http://localhost:8000/redeem/42?coins=100", method="POST")).status
    except HTTPError as e:
        return e.code


with ThreadPoolExecutor(max_workers=20) as pool:
    codes = list(pool.map(spend, range(20)))
print(f"200: {codes.count(200)}, 409: {codes.count(409)}, coins left: {r.get('coins:42')}")
