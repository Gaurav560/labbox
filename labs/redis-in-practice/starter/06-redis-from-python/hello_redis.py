"""Chapter 6: your first Python program that talks to Redis. Run it from this folder:

    python3 hello_redis.py
"""
import os

import redis

# One connection, opened once. REDIS_HOST is "redis" in this lab.
r = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"))

r.set("greeting", "Hello from Python")
print(r.get("greeting"))  # bytes: b'Hello from Python'

# decode_responses=True turns every answer into a normal str.
r = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"), decode_responses=True)
print(r.get("greeting"))  # str: Hello from Python
print(r.get("no:such:key"))  # a missing key is None
