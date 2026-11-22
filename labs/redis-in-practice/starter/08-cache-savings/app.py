"""Basket's price service, now measuring itself (chapter 8). Run it from this folder:

    uvicorn app:app --host 0.0.0.0 --port 8000 --reload

Try it from a second terminal:  curl localhost:8000/price/rice   and   curl localhost:8000/savings
"""
import os

import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from catalogue import PRICES, RUPEES_PER_CALL, SECONDS_PER_CALL, lookup_price

app = FastAPI()
r = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"), decode_responses=True)


@app.get("/price/{item}")
def price(item: str):
    """Cache-aside, as you wrote it in chapter 7."""
    key = f"price:{item}"
    cached = r.get(key)
    if cached is not None:
        # TODO (task hit_counter): count every hit in stats:price:hits, and every miss (below) in
        # stats:price:misses, so you can see how well the cache works.
        return {"item": item, "price": int(cached)}
    found = lookup_price(item)
    if found is None:
        raise HTTPException(status_code=404, detail=f"No {item} in the catalogue")
    r.set(key, found, ex=60)
    return {"item": item, "price": found}


@app.get("/savings")
def savings():
    # TODO (task savings_report): report what the cache saved, from the two counters:
    # {"hits": ..., "misses": ..., "hit_rate": hits / (hits + misses), rounded to 3 places (0 with no reads),
    #  "seconds_saved": hits * SECONDS_PER_CALL, "rupees_saved": hits * RUPEES_PER_CALL, both rounded to 2}
    raise HTTPException(status_code=501, detail="Not written yet")


class NewPrice(BaseModel):
    price: int


@app.put("/price/{item}")
def set_price(item: str, body: NewPrice):
    if item not in PRICES:
        raise HTTPException(status_code=404, detail=f"No {item} in the catalogue")
    PRICES[item] = body.price
    r.delete(f"price:{item}")
    return {"item": item, "price": body.price}
