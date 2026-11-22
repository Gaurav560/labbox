"""Basket's price service on sale day (chapter 9). Run it from this folder:

    uvicorn app:app --host 0.0.0.0 --port 8000 --reload

Watch a stampede from a second terminal:  python3 stampede.py paneer
"""
import os
import random
import time

import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from catalogue import PRICES, lookup_price

app = FastAPI()
r = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"), decode_responses=True)


def ask_catalogue(item: str, key: str) -> dict:
    found = lookup_price(item)
    if found is None:
        raise HTTPException(status_code=404, detail=f"No {item} in the catalogue")
    # A lifetime between 45 and 60 seconds: prices cached together no longer expire together.
    r.set(key, found, ex=random.randint(45, 60))
    r.incr("stats:price:misses")
    return {"item": item, "price": found}


@app.get("/price/{item}")
def price(item: str):
    """Cache-aside with hit and miss counters, as you wrote them in chapters 7 and 8."""
    key = f"price:{item}"
    cached = r.get(key)
    if cached is not None:
        r.incr("stats:price:hits")
        return {"item": item, "price": int(cached)}
    lock = f"lock:{key}"
    # Only the request that takes the lock asks the catalogue. The lock expires on its own after
    # 5 seconds, so a crashed request cannot block everyone forever.
    if r.set(lock, "1", nx=True, ex=5):
        try:
            return ask_catalogue(item, key)
        finally:
            r.delete(lock)
    # Someone else is asking the catalogue right now: wait for its answer to appear in Redis.
    for _ in range(50):
        time.sleep(0.1)
        cached = r.get(key)
        if cached is not None:
            r.incr("stats:price:hits")
            return {"item": item, "price": int(cached)}
    return ask_catalogue(item, key)  # the lock holder failed: ask ourselves


class NewPrice(BaseModel):
    price: int


@app.put("/price/{item}")
def set_price(item: str, body: NewPrice):
    if item not in PRICES:
        raise HTTPException(status_code=404, detail=f"No {item} in the catalogue")
    PRICES[item] = body.price
    r.delete(f"price:{item}")
    return {"item": item, "price": body.price}
