"""Book Point's quotes API for partners. Two copies run behind a load balancer: start them with
bash run.sh, then call http://lb:8080/quote with an X-API-Key header."""
import os
import random
import time

import redis
from fastapi import FastAPI, Header, HTTPException

app = FastAPI()
r = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"), decode_responses=True)

PER_KEY_LIMIT = 10  # requests per second for one API key
GLOBAL_LIMIT = 50  # requests per second for all keys together

QUOTES = [
    "Read first, code second.",
    "A cache is a promise you have to keep.",
    "Every queue is a backlog with good manners.",
    "Measure twice, deploy once.",
]


def allow(api_key: str) -> bool:
    """True if this request may go through."""
    second = int(time.time())
    key, total = f"rl:key:{api_key}:{second}", f"rl:all:{second}"
    pipe = r.pipeline()
    pipe.incr(key)
    pipe.expire(key, 2)
    pipe.incr(total)
    pipe.expire(total, 2)
    per_key, _, everyone, _ = pipe.execute()
    return per_key <= PER_KEY_LIMIT and everyone <= GLOBAL_LIMIT


@app.get("/health")
def health():
    return {"ok": True, "port": os.environ.get("PORT")}


@app.get("/quote")
def quote(x_api_key: str = Header(...)):
    if not allow(x_api_key):
        raise HTTPException(status_code=429, detail="Too many requests. Slow down.", headers={"Retry-After": "1"})
    return {"quote": random.choice(QUOTES), "served_by": os.environ.get("PORT")}
