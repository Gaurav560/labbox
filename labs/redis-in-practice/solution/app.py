"""Brew Point menu service.

Run it:  uvicorn app:app --host 0.0.0.0 --port 8000 --reload
Try it:  curl localhost:8000/price/samosa      curl -X POST localhost:8000/otp/9876543210
"""
import os
import time

import redis
from fastapi import FastAPI, HTTPException

app = FastAPI()
r = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"), decode_responses=True)

PRICES = {"filter coffee": 30, "cold coffee": 40, "vada pav": 25, "samosa": 20, "poha": 35}


def slow_price_lookup(item: str) -> int:
    """The old billing system: always right, but every call takes 1.5 seconds."""
    time.sleep(1.5)
    if item not in PRICES:
        raise HTTPException(status_code=404, detail=f"No {item} on the menu")
    return PRICES[item]


@app.get("/price/{item}")
def price(item: str):
    key = f"price:{item}"
    cached = r.get(key)
    if cached is not None:
        return {"item": item, "price": int(cached)}
    value = slow_price_lookup(item)
    r.set(key, value, ex=60)
    return {"item": item, "price": value}


@app.post("/otp/{phone}")
def send_otp(phone: str):
    key = f"otp:count:{phone}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, 60)
    if count > 3:
        raise HTTPException(status_code=429, detail="Too many OTPs. Try again in a minute.")
    return {"sent": True, "phone": phone}
