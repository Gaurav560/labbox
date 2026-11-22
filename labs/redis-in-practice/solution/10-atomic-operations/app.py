"""Basket's login codes and coins (chapter 10). Run it from this folder:

    uvicorn app:app --host 0.0.0.0 --port 8000 --reload

Try it from a second terminal:  curl -X POST localhost:8000/otp/9000000001
"""
import os

import redis
from fastapi import FastAPI, HTTPException

app = FastAPI()
r = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"), decode_responses=True)


@app.post("/otp/{phone}")
def send_otp(phone: str):
    key = f"otp:count:{phone}"
    count = r.incr(key)  # one step: read, add one, write
    if count == 1:
        r.expire(key, 60)  # the first code of the minute starts the clock
    if count > 3:
        raise HTTPException(status_code=429, detail="Too many login codes. Try again in a minute.")
    return {"sent": True, "phone": phone}


# Check and spend in one step: Redis runs a script from start to finish, with nothing in between.
SPEND = r.register_script("""
local balance = tonumber(redis.call('GET', KEYS[1]) or '0')
local cost = tonumber(ARGV[1])
if balance < cost then return -1 end
return redis.call('DECRBY', KEYS[1], cost)
""")


@app.post("/redeem/{cid}")
def redeem(cid: int, coins: int = 100):
    """Spend Basket coins from coins:<cid>. Never below zero, even when many requests arrive at once."""
    left = SPEND(keys=[f"coins:{cid}"], args=[coins])
    if left < 0:
        raise HTTPException(status_code=409, detail="Not enough coins")
    return {"redeemed": coins, "left": left}
