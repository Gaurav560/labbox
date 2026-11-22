"""Basket's price service (chapter 7). Run it from this folder:

    uvicorn app:app --host 0.0.0.0 --port 8000 --reload

Try it from a second terminal:  curl localhost:8000/price/rice
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
    key = f"price:{item}"
    cached = r.get(key)
    if cached is not None:
        return {"item": item, "price": int(cached)}
    found = lookup_price(item)
    if found is None:
        raise HTTPException(status_code=404, detail=f"No {item} in the catalogue")
    r.set(key, found, ex=60)
    return {"item": item, "price": found}


class NewPrice(BaseModel):
    price: int


@app.put("/price/{item}")
def set_price(item: str, body: NewPrice):
    """The pricing team changes a price in the catalogue."""
    if item not in PRICES:
        raise HTTPException(status_code=404, detail=f"No {item} in the catalogue")
    PRICES[item] = body.price
    r.delete(f"price:{item}")
    return {"item": item, "price": body.price}
