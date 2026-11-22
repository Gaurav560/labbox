"""Basket's operations dashboard (chapter 17). Run it from this folder:

    uvicorn app:app --host 0.0.0.0 --port 8000 --reload

Try it from a second terminal:  curl localhost:8000/sessions/active
"""
import os

import redis
from fastapi import FastAPI

app = FastAPI()
r = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"), decode_responses=True)


@app.get("/sessions/active")
def active_sessions():
    """How many customers are signed in right now. The dashboard calls this every few seconds."""
    # TODO (task scan_not_keys): KEYS walks every key in one go, and Redis serves nobody else meanwhile.
    # Count the sessions in small steps instead, so other clients are served in between.
    return {"active": len(r.keys("session:*"))}
