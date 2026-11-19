"""Brew Point's menu service. One section per chapter; each TODO is a task.

Run it:   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
Try it:   curl localhost:8000/customers/42        curl localhost:8000/price/samosa
"""
import csv
import os
import time

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
    # TODO(profile_api): read the hash customer:<cid>. Answer 404 if there is no such customer,
    # otherwise {"id": cid, "name": ..., "visits": <a number>, "tier": ...}.
    raise HTTPException(status_code=501, detail="Not written yet")


@app.post("/import")
def import_sales():
    """Load data/sales.csv into the hash sales:import, field "<outlet>:<item>", value cups."""
    with open("data/sales.csv", newline="") as f:
        rows = list(csv.DictReader(f))
    # TODO(bulk_import): this works, but makes one round trip to Redis per row. Make it fast.
    for row in rows:
        r.hset("sales:import", f"{row['outlet']}:{row['item']}", row["cups"])
    return {"imported": len(rows)}


# ---------- chapter 6: caching for real ----------

@app.get("/price/{item}")
def price(item: str):
    # TODO(price_cache): look in Redis first (key price:<item>). On a miss, call slow_price_lookup
    # and keep the answer in Redis for 60 seconds.
    # TODO(stampede_lock): when the cache is empty and many requests arrive at once, only one of
    # them may call slow_price_lookup; the others wait for its answer.
    return {"item": item, "price": slow_price_lookup(item)}


class NewPrice(BaseModel):
    price: int


@app.put("/price/{item}")
def set_price(item: str, body: NewPrice):
    if item not in PRICES:
        raise HTTPException(status_code=404, detail=f"No {item} on the menu")
    PRICES[item] = body.price
    # TODO(price_invalidate): the cache still has the old price. Make the next read see the new one.
    return {"item": item, "price": body.price}


# ---------- chapter 7: atomic operations ----------

@app.post("/otp/{phone}")
def send_otp(phone: str):
    # TODO(otp_limit): at most 3 OTPs per phone number per minute. The 4th gets a 429.
    return {"sent": True, "phone": phone}


@app.post("/redeem/{cid}")
def redeem(cid: int, points: int = 100):
    """Spend loyalty points from loyalty:<cid>. Never below zero, even with many requests at once."""
    key = f"loyalty:{cid}"
    # TODO(redeem_points): this read-then-write races. Make the check and the spend one atomic step.
    balance = int(r.get(key) or 0)
    if balance < points:
        raise HTTPException(status_code=409, detail="Not enough points")
    time.sleep(0.02)  # checking the order for fraud (a slow call)
    r.set(key, balance - points)
    return {"redeemed": points, "left": balance - points}


# ---------- chapter 8: distributed locks ----------

@app.post("/book/{table}")
def book(table: int, customer: str):
    """Book a table for this evening. One table, one customer: the first to book wins."""
    key = f"booking:table:{table}"
    # TODO(book_once): two requests can both see "free" and both book. Make exactly one win.
    if r.exists(key):
        raise HTTPException(status_code=409, detail="Already booked")
    time.sleep(0.05)  # checking the customer's loyalty status (a slow call)
    r.set(key, customer)
    return {"table": table, "booked_for": customer}


class Release(BaseModel):
    token: str


@app.post("/locks/{name}/release")
def release_lock(name: str, body: Release):
    """Release lock:<name>, but only if we still hold it: the value is our token."""
    # TODO(safe_unlock): this deletes the lock even when someone else holds it now.
    r.delete(f"lock:{name}")
    return {"released": True}


# ---------- chapter 13: production habits ----------

@app.get("/sessions/active")
def active_sessions():
    """How many customers are logged in right now (the ops dashboard calls this every few seconds)."""
    # TODO(scan_not_keys): KEYS walks every key in one go while Redis serves nobody else.
    return {"active": len(r.keys("session:*"))}
