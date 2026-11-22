"""Basket's delivery slots (chapter 11). Run it from this folder:

    uvicorn app:app --host 0.0.0.0 --port 8000 --reload

Try it from a second terminal:  curl -X POST "localhost:8000/book/1800?customer=asha"
"""
import os
import time
import uuid

import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
r = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"), decode_responses=True)

# Delete the lock only if it still holds our token: compare and delete in one step.
UNLOCK = r.register_script("""
if redis.call('GET', KEYS[1]) == ARGV[1] then
  return redis.call('DEL', KEYS[1])
end
return 0
""")


@app.post("/book/{slot}")
def book(slot: int, customer: str):
    """Book a delivery slot. One rider, one slot: the first customer to book it wins."""
    key = f"booking:slot:{slot}"
    lock, token = f"lock:{key}", uuid.uuid4().hex
    if not r.set(lock, token, nx=True, px=2000):
        raise HTTPException(status_code=409, detail="Someone is booking this slot right now")
    try:
        if r.exists(key):
            raise HTTPException(status_code=409, detail="Already booked")
        time.sleep(0.05)  # checking that a rider is free (a slow call)
        r.set(key, customer)
        return {"slot": slot, "booked_for": customer}
    finally:
        UNLOCK(keys=[lock], args=[token])


class Release(BaseModel):
    token: str


@app.post("/locks/{name}/release")
def release_lock(name: str, body: Release):
    """Release lock:<name>, but only if we still hold it: its value is our token."""
    released = UNLOCK(keys=[f"lock:{name}"], args=[body.token])
    return {"released": bool(released)}
