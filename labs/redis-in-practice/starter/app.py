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
    # TODO(price_cache): look in Redis first (key price:<item>). On a miss, call slow_price_lookup
    # and keep the answer in Redis for 60 seconds.
    return {"item": item, "price": slow_price_lookup(item)}


@app.post("/otp/{phone}")
def send_otp(phone: str):
    # TODO(otp_limit): at most 3 OTPs per phone number per minute. The 4th gets a 429.
    return {"sent": True, "phone": phone}
