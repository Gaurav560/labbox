"""Basket's login codes and coins (chapter 10). Run it from this folder:

    uvicorn app:app --host 0.0.0.0 --port 8000 --reload

Try it from a second terminal:  curl -X POST localhost:8000/otp/9000000001
"""
import os
import time

import redis
from fastapi import FastAPI, HTTPException

app = FastAPI()
r = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"), decode_responses=True)


@app.post("/otp/{phone}")
def send_otp(phone: str):
    # TODO (task otp_limit): at most 3 login codes per phone number per minute. The 4th gets a 429.
    return {"sent": True, "phone": phone}


@app.post("/redeem/{cid}")
def redeem(cid: int, coins: int = 100):
    """Spend Basket coins from coins:<cid>. Never below zero, even when many requests arrive at once."""
    key = f"coins:{cid}"
    balance = int(r.get(key) or 0)
    # TODO (task redeem_points): between this GET and the DECRBY below, another request can spend the
    # same coins. Make the check and the spend one single step in Redis.
    if balance < coins:
        raise HTTPException(status_code=409, detail="Not enough coins")
    time.sleep(0.1)  # checking the order with the payments service
    left = r.decrby(key, coins)
    return {"redeemed": coins, "left": left}
