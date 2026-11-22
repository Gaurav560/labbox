"""Basket's catalogue service: the source of truth for every price.

It is always right, but it is slow: every question takes 1.5 seconds, and the partner who runs it bills
Basket Rs 0.10 per call. Each call is counted in Redis under catalogue:calls, so you can watch how often
it is asked. You never change this file; your app decides how often to call it.
"""
import os
import time

import redis

r = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"), decode_responses=True)

PRICES = {"rice": 60, "dal": 120, "mangoes": 300, "eggs": 84, "atta": 55, "onions": 40, "paneer": 90, "bread": 45}
SECONDS_PER_CALL = 1.5
RUPEES_PER_CALL = 0.10


def lookup_price(item: str) -> int | None:
    """The price of one item in rupees, or None when the catalogue has no such item."""
    r.incr("catalogue:calls")
    time.sleep(SECONDS_PER_CALL)
    return PRICES.get(item)
