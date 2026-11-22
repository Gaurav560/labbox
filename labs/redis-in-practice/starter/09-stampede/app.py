"""Basket's price service on sale day (chapter 9). Run it from this folder:

    uvicorn app:app --host 0.0.0.0 --port 8000 --reload

Watch a stampede from a second terminal:  python3 stampede.py paneer
"""
import os

import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from catalogue import PRICES, lookup_price

app = FastAPI()
r = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"), decode_responses=True)


@app.get("/price/{item}")
def price(item: str):
    """Cache-aside with hit and miss counters, as you wrote them in chapters 7 and 8."""
    key = f"price:{item}"
    cached = r.get(key)
    if cached is not None:
        r.incr("stats:price:hits")
        return {"item": item, "price": int(cached)}
    # TODO (task stampede_lock): when the cache is empty and many requests arrive at once, only one of
    # them may ask the catalogue; the others wait a moment and read its answer from Redis.
    found = lookup_price(item)
    if found is None:
        raise HTTPException(status_code=404, detail=f"No {item} in the catalogue")
    # TODO (task jitter_ttl): every price expires after exactly 60 seconds, so prices cached together
    # also expire together. Give each one a random lifetime between 45 and 60 seconds instead.
    r.set(key, found, ex=60)
    r.incr("stats:price:misses")
    return {"item": item, "price": found}


class NewPrice(BaseModel):
    price: int


@app.put("/price/{item}")
def set_price(item: str, body: NewPrice):
    if item not in PRICES:
        raise HTTPException(status_code=404, detail=f"No {item} in the catalogue")
    PRICES[item] = body.price
    r.delete(f"price:{item}")
    return {"item": item, "price": body.price}
