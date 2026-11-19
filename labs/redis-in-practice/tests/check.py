"""Live checks for redis-in-practice: read the learner's Redis, and call their running app over HTTP.
Chapter 1 is checked by what is in Redis; chapter 2 by how the app behaves (timing and status codes)."""
import json
import time

import redis
import requests

APP = "http://workspace:8000"
NOT_RUNNING = "Your app is not answering on port 8000. Start it in a terminal: uvicorn app:app --host 0.0.0.0 --port 8000 --reload"


def report(task, passed, message, expected=None, actual=None):
    r = {"task": task, "passed": passed, "message": message}
    if expected is not None:
        r["expected"], r["actual"] = expected, actual
    print("@@RESULT " + json.dumps(r), flush=True)


try:
    r = redis.Redis(host="redis", decode_responses=True, socket_timeout=5)
    r.ping()
except Exception as e:
    for t in ("menu_hash", "otp_expiry", "top_sellers", "price_cache", "otp_limit"):
        report(t, False, f"Could not reach Redis: {e}")
    raise SystemExit(0)


# ---------- chapter 1: redis-cli ----------

def menu_hash():
    want = {"filter coffee": "30", "cold coffee": "40", "vada pav": "25"}
    kind = r.type("menu")
    if kind == "none":
        return report("menu_hash", False, "There is no key named menu yet.")
    if kind != "hash":
        return report("menu_hash", False, f"menu is a {kind}, not a hash. DEL menu and make it with HSET.", "hash", kind)
    got = r.hgetall("menu")
    if got != want:
        return report("menu_hash", False, "The menu hash has different fields or prices.", json.dumps(want), json.dumps(got))
    report("menu_hash", True, "Three items, three prices, one key.")


def otp_expiry():
    key = "otp:9876543210"
    value, ttl = r.get(key) if r.type(key) == "string" else None, r.ttl(key)
    if ttl == -2:
        return report("otp_expiry", False, f"{key} does not exist (or it already expired: set it again).")
    if value != "4821":
        return report("otp_expiry", False, f"{key} should hold the OTP 4821.", "4821", str(value))
    if ttl == -1:
        return report("otp_expiry", False, f"{key} never expires. An OTP must disappear on its own.", "a TTL of 300 s or less", "no expiry")
    if ttl > 300:
        return report("otp_expiry", False, f"{key} lives too long.", "300 s or less", f"{ttl} s")
    report("otp_expiry", True, f"The OTP disappears in {ttl} seconds.")


def top_sellers():
    want = [["filter coffee", 120.0], ["vada pav", 80.0], ["cold coffee", 50.0]]
    kind = r.type("sales:today")
    if kind == "none":
        return report("top_sellers", False, "There is no key named sales:today yet.")
    if kind != "zset":
        return report("top_sellers", False, f"sales:today is a {kind}, not a sorted set.", "zset", kind)
    got = [[m, s] for m, s in r.zrevrange("sales:today", 0, -1, withscores=True)]
    if got != want:
        return report("top_sellers", False, "The scores are not right yet (did cold coffee get its 5 extra?).", json.dumps(want), json.dumps(got))
    report("top_sellers", True, "Best sellers, in order, kept by Redis.")


# ---------- chapter 2: the app ----------

def app_up():
    try:
        requests.get(f"{APP}/docs", timeout=3)
        return True
    except requests.RequestException:
        return False


def price_cache():
    item, key = "poha", "price:poha"
    r.delete(key)  # start cold, so the first call must go to the slow lookup
    try:
        t0 = time.monotonic()
        first = requests.get(f"{APP}/price/{item}", timeout=10)
        cold = time.monotonic() - t0
        t0 = time.monotonic()
        second = requests.get(f"{APP}/price/{item}", timeout=10)
        warm = time.monotonic() - t0
    except requests.RequestException as e:
        return report("price_cache", False, f"Calling /price/{item} failed: {e}")
    want = {"item": item, "price": 35}
    for resp in (first, second):
        if resp.status_code != 200 or resp.json() != want:
            return report("price_cache", False, f"/price/{item} gave the wrong answer.", json.dumps(want), f"{resp.status_code} {resp.text[:200]}")
    if warm > 0.3:
        return report("price_cache", False, f"The second call still took {warm:.2f} s, so nothing was cached.", "< 0.3 s", f"{warm:.2f} s")
    if cold < 1.0:
        return report("price_cache", False, "The first call was fast even with an empty cache. Call slow_price_lookup on a miss.")
    ttl = r.ttl(key)
    if ttl == -2:
        return report("price_cache", False, f"Nothing was stored under {key}.", key, "missing")
    if ttl == -1 or ttl > 60:
        return report("price_cache", False, f"{key} must expire within 60 seconds, so price changes show up.", "<= 60 s", "no expiry" if ttl == -1 else f"{ttl} s")
    report("price_cache", True, f"First call {cold:.2f} s, second {warm * 1000:.0f} ms.")


def otp_limit():
    phone = "9000000001"
    key = f"otp:count:{phone}"
    r.delete(key)
    try:
        codes = [requests.post(f"{APP}/otp/{phone}", timeout=5).status_code for _ in range(4)]
    except requests.RequestException as e:
        return report("otp_limit", False, f"Calling /otp/{phone} failed: {e}")
    finally:
        ttl = r.ttl(key)
        r.delete(key)
    if codes != [200, 200, 200, 429]:
        return report("otp_limit", False, "Four OTPs in a row should give three 200s, then a 429.", "[200, 200, 200, 429]", str(codes))
    if ttl == -2:
        return report("otp_limit", False, f"The count must live in Redis under {key}.", key, "missing")
    if ttl == -1 or ttl > 60:
        return report("otp_limit", False, f"{key} must expire within a minute, or the phone is blocked forever.", "<= 60 s", "no expiry" if ttl == -1 else f"{ttl} s")
    report("otp_limit", True, "Three OTPs go through, the fourth gets 429, and the count resets in a minute.")


menu_hash()
otp_expiry()
top_sellers()
if app_up():
    price_cache()
    otp_limit()
else:
    report("price_cache", False, NOT_RUNNING)
    report("otp_limit", False, NOT_RUNNING)
