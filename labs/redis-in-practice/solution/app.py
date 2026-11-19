"""Brew Point's menu service. One section per chapter; each TODO is a task.

Run it:   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
Try it:   curl localhost:8000/customers/42        curl localhost:8000/price/samosa
"""
import csv
import os
import time
import uuid

import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
# decode_responses=True: Redis answers with str instead of bytes.
r = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"), decode_responses=True)

# The old billing system: always right, but slow. The source of truth for prices.
PRICES = {"filter coffee": 30, "cold coffee": 40, "vada pav": 25, "samosa": 20, "poha": 35}


def slow_price_lookup(item: str) -> int:
    """Every call takes 1.5 seconds and is counted in billing:calls (the billing team watches it)."""
    r.incr("billing:calls")
    time.sleep(1.5)
    if item not in PRICES:
        raise HTTPException(status_code=404, detail=f"No {item} on the menu")
    return PRICES[item]


# ---------- chapter 5: Redis from Python ----------

@app.get("/customers/{cid}")
def customer(cid: int):
    data = r.hgetall(f"customer:{cid}")
    if not data:
        raise HTTPException(status_code=404, detail="No such customer")
    return {"id": cid, "name": data.get("name"), "visits": int(data.get("visits", 0)), "tier": data.get("tier")}


@app.post("/import")
def import_sales():
    """Load data/sales.csv into the hash sales:import, field "<outlet>:<item>", value cups."""
    with open("data/sales.csv", newline="") as f:
        rows = list(csv.DictReader(f))
    pipe = r.pipeline(transaction=False)
    for row in rows:
        pipe.hset("sales:import", f"{row['outlet']}:{row['item']}", row["cups"])
    pipe.execute()
    return {"imported": len(rows)}


# ---------- chapter 6: caching for real ----------

@app.get("/price/{item}")
def price(item: str):
    key = f"price:{item}"
    cached = r.get(key)
    if cached is not None:
        return {"item": item, "price": int(cached)}
    # Only one request rebuilds the cache; the others wait for it (at most 3 seconds).
    if r.set(f"lock:{key}", "1", nx=True, ex=5):
        try:
            value = slow_price_lookup(item)
            r.set(key, value, ex=60)
            return {"item": item, "price": value}
        finally:
            r.delete(f"lock:{key}")
    for _ in range(60):
        time.sleep(0.05)
        cached = r.get(key)
        if cached is not None:
            return {"item": item, "price": int(cached)}
    raise HTTPException(status_code=503, detail="Price is being refreshed, try again")


class NewPrice(BaseModel):
    price: int


@app.put("/price/{item}")
def set_price(item: str, body: NewPrice):
    if item not in PRICES:
        raise HTTPException(status_code=404, detail=f"No {item} on the menu")
    PRICES[item] = body.price
    r.delete(f"price:{item}")
    return {"item": item, "price": body.price}


# ---------- chapter 7: atomic operations ----------

@app.post("/otp/{phone}")
def send_otp(phone: str):
    key = f"otp:count:{phone}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, 60)
    if count > 3:
        raise HTTPException(status_code=429, detail="Too many OTPs. Try again in a minute.")
    return {"sent": True, "phone": phone}


# Check and spend in one step: Redis runs a script start to finish, with nothing in between.
SPEND = r.register_script("""
local balance = tonumber(redis.call('GET', KEYS[1]) or '0')
local cost = tonumber(ARGV[1])
if balance < cost then return -1 end
return redis.call('DECRBY', KEYS[1], cost)
""")


@app.post("/redeem/{cid}")
def redeem(cid: int, points: int = 100):
    """Spend loyalty points from loyalty:<cid>. Never below zero, even with many requests at once."""
    left = SPEND(keys=[f"loyalty:{cid}"], args=[points])
    if left < 0:
        raise HTTPException(status_code=409, detail="Not enough points")
    return {"redeemed": points, "left": left}


# ---------- chapter 8: distributed locks ----------

@app.post("/book/{table}")
def book(table: int, customer: str):
    """Book a table for this evening. One table, one customer: the first to book wins."""
    key = f"booking:table:{table}"
    lock, token = f"lock:{key}", uuid.uuid4().hex
    if not r.set(lock, token, nx=True, px=2000):
        raise HTTPException(status_code=409, detail="Someone is booking this table right now")
    try:
        if r.exists(key):
            raise HTTPException(status_code=409, detail="Already booked")
        time.sleep(0.05)  # checking the customer's loyalty status (a slow call)
        r.set(key, customer)
        return {"table": table, "booked_for": customer}
    finally:
        UNLOCK(keys=[lock], args=[token])


# Delete the lock only if it still holds our token: compare and delete in one step.
UNLOCK = r.register_script("""
if redis.call('GET', KEYS[1]) == ARGV[1] then
  return redis.call('DEL', KEYS[1])
end
return 0
""")


class Release(BaseModel):
    token: str


@app.post("/locks/{name}/release")
def release_lock(name: str, body: Release):
    """Release lock:<name>, but only if we still hold it: the value is our token."""
    released = UNLOCK(keys=[f"lock:{name}"], args=[body.token])
    return {"released": bool(released)}
