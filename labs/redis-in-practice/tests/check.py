"""Live checks for redis-in-practice: read the learner's Redis, and call their running app over HTTP.
Chapters 1 to 4 are checked by what is in Redis; chapter 5 by how the app behaves (timing, status codes)."""
import json
import time

import redis
import requests

APP = "http://workspace:8000"
TASKS = ("first_keys", "cups_counter", "clean_up", "otp_expiry", "session_ttl", "keep_forever", "menu_hash",
         "customer_profile", "order_queue", "unique_visitors", "common_customers", "top_sellers", "price_cache", "otp_limit")
SESSION = '{"customer": 42, "outlet": "andheri"}'  # what setup/02.sh stored
ANDHERI = {"asha", "ravi", "meera", "kabir", "priya", "dev"}
BANDRA = {"ravi", "sana", "priya", "arjun", "dev", "zoya"}
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
    for t in TASKS:
        report(t, False, f"Could not reach Redis: {e}")
    raise SystemExit(0)


def kind(key):
    return r.type(key)


# ---------- chapter 1: what Redis is ----------

def first_keys():
    want = {"shop:name": "Brew Point", "shop:city": "Pune"}
    for key, value in want.items():
        if kind(key) == "none":
            return report("first_keys", False, f"There is no key named {key} yet.")
        if kind(key) != "string":
            return report("first_keys", False, f"{key} should hold plain text, not a {kind(key)}.", "string", kind(key))
        if r.get(key) != value:
            return report("first_keys", False, f"{key} holds something else.", value, r.get(key))
    report("first_keys", True, "The shop has a name and a city.")


def cups_counter():
    if kind("cups:sold") == "none":
        return report("cups_counter", False, "There is no cups:sold counter yet. The first INCR creates it.")
    if r.get("cups:sold") != "3":
        return report("cups_counter", False, "cups:sold should count the three cups.", "3", r.get("cups:sold"))
    beans = r.get("beans:grams")
    if beans is None:
        return report("cups_counter", False, "beans:grams is gone. Press Reset lab to get the stock back.")
    if beans != "750":
        return report("cups_counter", False, "The bean stock should be 250 grams lower than the 1000 it started at.", "750", beans)
    report("cups_counter", True, "Three cups counted, 250 grams of beans used.")


def clean_up():
    left = sorted(r.scan_iter("tmp:import:*"))
    if left:
        return report("clean_up", False, f"{len(left)} temporary key(s) are still there.", "none", ", ".join(left))
    if r.get("beans:grams") is None:
        return report("clean_up", False, "beans:grams was deleted too. Only the tmp:import keys had to go (Reset lab brings it back).")
    report("clean_up", True, "The leftovers are gone; everything else is untouched.")


# ---------- chapter 2: keys that expire ----------

def session_ttl():
    key = "session:7f3a"
    ttl = r.ttl(key)
    if ttl == -2:
        return report("session_ttl", False, f"{key} is gone. Press Reset lab to get it back.")
    if r.get(key) != SESSION:
        return report("session_ttl", False, f"The value of {key} changed. Add a timer without writing the key again.", SESSION, r.get(key))
    if ttl == -1:
        return report("session_ttl", False, f"{key} still has no timer.", "about 1800 seconds", "no timer")
    if ttl > 1800 or ttl < 60:
        return report("session_ttl", False, f"{key} should live for 30 minutes.", "1800 seconds or a little less", f"{ttl} seconds")
    report("session_ttl", True, f"The session now ends on its own, in {ttl // 60} minutes.")


def keep_forever():
    key = "promo:diwali"
    ttl = r.ttl(key)
    if ttl == -2:
        return report("keep_forever", False, f"{key} is gone. Press Reset lab to get it back.")
    if r.get(key) != "20% off filter coffee":
        return report("keep_forever", False, f"The value of {key} changed.", "20% off filter coffee", r.get(key))
    if ttl != -1:
        return report("keep_forever", False, f"{key} still has a timer.", "no timer (-1)", f"{ttl} seconds left")
    report("keep_forever", True, "The promo is here to stay.")


# ---------- chapter 3: hashes and lists ----------

def customer_profile():
    key = "customer:42"
    if kind(key) == "none":
        return report("customer_profile", False, f"There is no {key} yet.")
    if kind(key) != "hash":
        return report("customer_profile", False, f"{key} is a {kind(key)}, not a hash.", "hash", kind(key))
    want = {"name": "Asha", "visits": "8", "tier": "gold"}
    got = r.hgetall(key)
    if got != want:
        return report("customer_profile", False, "Asha's profile is not right yet (7 visits plus the one today).", json.dumps(want), json.dumps(got))
    report("customer_profile", True, "Asha: 8 visits, gold tier, all in one hash.")


def order_queue():
    key = "orders:pending"
    if kind(key) == "none":
        return report("order_queue", False, "There is no orders:pending list yet.")
    if kind(key) != "list":
        return report("order_queue", False, f"{key} is a {kind(key)}, not a list.", "list", kind(key))
    got = r.lrange(key, 0, -1)
    if got != ["o3", "o2"]:
        return report("order_queue", False, "The queue should still hold the two newest orders, newest first.", '["o3", "o2"]', json.dumps(got))
    report("order_queue", True, "First in, first out: o1 is being made, o2 and o3 wait.")


# ---------- chapter 4: sets and sorted sets ----------

def unique_visitors():
    key = "visitors:today"
    if kind(key) == "none":
        return report("unique_visitors", False, "There is no visitors:today set yet.")
    if kind(key) != "set":
        return report("unique_visitors", False, f"{key} is a {kind(key)}, not a set.", "set", kind(key))
    got = r.smembers(key)
    if got != {"asha", "ravi", "meera"}:
        return report("unique_visitors", False, "The set should hold each of this morning's visitors once.", "asha, meera, ravi", ", ".join(sorted(got)))
    report("unique_visitors", True, "Five visits, three people.")


def common_customers():
    if r.smembers("customers:andheri") != ANDHERI or r.smembers("customers:bandra") != BANDRA:
        return report("common_customers", False, "The outlet sets were changed. Press Reset lab to get them back.")
    key = "customers:both"
    if kind(key) == "none":
        return report("common_customers", False, "There is no customers:both set yet.")
    if kind(key) != "set":
        return report("common_customers", False, f"{key} is a {kind(key)}, not a set.", "set", kind(key))
    want, got = ANDHERI & BANDRA, r.smembers(key)
    if got != want:
        return report("common_customers", False, "customers:both should hold exactly the people in both outlet sets.", ", ".join(sorted(want)), ", ".join(sorted(got)))
    report("common_customers", True, f"{len(want)} loyal customers visit both outlets.")


# ---------- from the first version: the menu (ch 3), the OTP (ch 2), best sellers (ch 4) ----------

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


# ---------- chapter 5: a cache and a rate limiter (the app) ----------

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


for check in (first_keys, cups_counter, clean_up, otp_expiry, session_ttl, keep_forever, menu_hash,
              customer_profile, order_queue, unique_visitors, common_customers, top_sellers):
    check()
if app_up():
    price_cache()
    otp_limit()
else:
    report("price_cache", False, NOT_RUNNING)
    report("otp_limit", False, NOT_RUNNING)
