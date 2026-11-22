"""Basket's delivery slots (chapter 11). Run it from this folder:

    uvicorn app:app --host 0.0.0.0 --port 8000 --reload

Try it from a second terminal:  curl -X POST "localhost:8000/book/1800?customer=asha"
"""
import os
import time

import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
r = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"), decode_responses=True)


@app.post("/book/{slot}")
def book(slot: int, customer: str):
    """Book a delivery slot. One rider, one slot: the first customer to book it wins."""
    key = f"booking:slot:{slot}"
    # TODO (task book_once): two customers can both pass this check before either one writes.
    # Take a lock first (SET with NX and an expiry), so only one request books at a time.
    if r.exists(key):
        raise HTTPException(status_code=409, detail="Already booked")
    time.sleep(0.05)  # checking that a rider is free (a slow call)
    r.set(key, customer)
    return {"slot": slot, "booked_for": customer}


class Release(BaseModel):
    token: str


@app.post("/locks/{name}/release")
def release_lock(name: str, body: Release):
    """Release lock:<name>, but only if we still hold it: its value is our token."""
    # TODO (task safe_unlock): this deletes the lock even when somebody else holds it now.
    # Delete it only if its value is still body.token, as one single step.
    released = r.delete(f"lock:{name}")
    return {"released": bool(released)}
