"""Live checks for redis-in-practice: read the learner's Redis, and call their running app over HTTP.

Chapters 1 to 5 and 12 to 16 are checked by what is in Redis; chapters 6 to 11 and 17 by how the app
behaves: answers, round trips, and real races (many requests at the same moment). Only the tasks in
LABBOX_TASKS run (all of them when it is not set), so checking one chapter never touches another.
"""
import json
import os
import random
import time
from concurrent.futures import ThreadPoolExecutor

from redis.crc import key_slot

import redis
import requests

APP = "http://workspace:8000"
OOM = "Redis refuses writes (out of memory): fix the chapter 14 incident first."
SESSION = '{"customer": 42, "store": "kothrud"}'  # what setup/03.sh stored
PROMO = "20% off mangoes"
KOTHRUD = {"asha", "ravi", "meera", "kabir", "priya", "dev"}
BANER = {"ravi", "sana", "priya", "arjun", "dev", "zoya"}
# The folder of each app task's chapter, for "start this chapter's app" messages.
FOLDER = {"profile_api": "06-redis-from-python", "bulk_import": "06-redis-from-python",
          "price_cache": "07-caching", "price_invalidate": "07-caching",
          "hit_counter": "08-cache-savings", "savings_report": "08-cache-savings",
          "stampede_lock": "09-stampede", "jitter_ttl": "09-stampede",
          "otp_limit": "10-atomic-operations", "redeem_points": "10-atomic-operations",
          "book_once": "11-locks", "safe_unlock": "11-locks", "scan_not_keys": "17-capstone"}


def start_hint(task):
    return f"cd /workspace/{FOLDER[task]} && uvicorn app:app --host 0.0.0.0 --port 8000 --reload"


def report(task, passed, message, expected=None, actual=None):
    r = {"task": task, "passed": passed, "message": message}
    if expected is not None:
        r["expected"], r["actual"] = expected, actual
    print("@@RESULT " + json.dumps(r), flush=True)


WANTED = {t for t in os.environ.get("LABBOX_TASKS", "").split(",") if t}

try:
    r = redis.Redis(host="redis", decode_responses=True, socket_timeout=5)
    r.ping()
except Exception as e:
    for t in sorted(WANTED) or ["first_keys"]:
        report(t, False, f"Could not reach Redis: {e}")
    raise SystemExit(0)


def kind(key):
    return r.type(key)


# ---------- chapter 1: why Redis exists ----------

def number(key, cast):
    value = r.get(key)
    try:
        return cast(value) if value is not None else None
    except ValueError:
        return "bad"


def measure_latency():
    ms = number("bench:latency_ms", float)
    if ms is None:
        return report("measure_latency", False, "There is no bench:latency_ms yet. Run redis-cli --latency for a few seconds, "
                      "stop it with Ctrl+C, and store the avg it printed.")
    if ms == "bad":
        return report("measure_latency", False, "bench:latency_ms should be just the number of milliseconds, like 0.21.",
                      "a number such as 0.21", r.get("bench:latency_ms"))
    if not 0.005 <= ms <= 50:
        return report("measure_latency", False, "That is not a latency redis-cli would print here (it measures in milliseconds).",
                      "between 0.005 and 50", str(ms))
    report("measure_latency", True, f"A round trip to Redis took about {ms} ms: the time to ask and get an answer, network included.")


def measure_redis():
    for key in ("bench:get_per_sec", "bench:set_per_sec"):
        n = number(key, lambda v: int(float(v)))
        if n is None:
            return report("measure_redis", False, f"There is no {key} yet. Run the redis-benchmark command from the lesson and "
                          "store the requests per second it printed.")
        if n == "bad":
            return report("measure_redis", False, f"{key} should be a plain number of requests per second, like 85000.",
                          "a whole number", r.get(key))
        if not 2_000 <= n <= 10_000_000:
            return report("measure_redis", False, f"{key} is not a number redis-benchmark would print for one Redis.",
                          "thousands to millions per second", str(n))
    gets = int(float(r.get("bench:get_per_sec")))
    report("measure_redis", True, f"About {gets:,} GETs a second from one Redis: more than {gets * 86_400 // 1_000_000:,} million a day.")


# ---------- chapter 2: your first keys ----------

def first_keys():
    want = {"shop:name": "Basket", "shop:city": "Pune"}
    for key, value in want.items():
        if kind(key) == "none":
            return report("first_keys", False, f"There is no key named {key} yet.")
        if kind(key) != "string":
            return report("first_keys", False, f"{key} should hold plain text, not a {kind(key)}.", "string", kind(key))
        if r.get(key) != value:
            return report("first_keys", False, f"{key} holds something else (capital letters matter).", value, r.get(key))
    report("first_keys", True, "Basket has a name and a city, each under its own key.")


def cups_counter():
    if kind("orders:today") == "none":
        return report("cups_counter", False, "There is no orders:today counter yet. The first INCR creates it.")
    if r.get("orders:today") != "3":
        return report("cups_counter", False, "orders:today should count the three orders, one INCR each.", "3", r.get("orders:today"))
    eggs = r.get("stock:eggs")
    if eggs is None:
        return report("cups_counter", False, "stock:eggs is gone. Press Reset lab to get the stock back.")
    if eggs != "108":
        return report("cups_counter", False, "The egg stock should be 12 lower than the 120 it started at.", "108", eggs)
    report("cups_counter", True, "Three orders counted and a dozen eggs off the stock, each in one safe step.")


def clean_up():
    left = sorted(r.scan_iter("tmp:import:*"))
    if left:
        return report("clean_up", False, f"{len(left)} temporary key(s) are still there.", "none", ", ".join(left))
    if r.get("stock:eggs") is None:
        return report("clean_up", False, "stock:eggs was deleted too. Only the tmp:import keys had to go (Reset lab brings it back).")
    report("clean_up", True, "The leftovers are gone, and everything else is untouched.")


# ---------- chapter 3: keys that expire ----------

def otp_expiry():
    key = "otp:9876543210"
    value, ttl = r.get(key) if r.type(key) == "string" else None, r.ttl(key)
    if ttl == -2:
        return report("otp_expiry", False, f"{key} does not exist (or it already expired: set it again).")
    if value != "4821":
        return report("otp_expiry", False, f"{key} should hold the login code 4821.", "4821", str(value))
    if ttl == -1:
        return report("otp_expiry", False, f"{key} never expires. A login code must disappear on its own.", "a TTL of 300 s or less", "no expiry")
    if ttl > 300:
        return report("otp_expiry", False, f"{key} lives too long.", "300 s or less", f"{ttl} s")
    report("otp_expiry", True, f"The login code disappears by itself in {ttl} seconds.")


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
    if r.get(key) != PROMO:
        return report("keep_forever", False, f"The value of {key} changed.", PROMO, r.get(key))
    if ttl != -1:
        return report("keep_forever", False, f"{key} still has a timer.", "no timer (-1)", f"{ttl} seconds left")
    report("keep_forever", True, "The promo is here to stay.")


# ---------- chapter 4: hashes and lists ----------

def menu_hash():
    want = {"rice": "60", "dal": "120", "mangoes": "300"}
    if kind("catalogue") == "none":
        return report("menu_hash", False, "There is no key named catalogue yet.")
    if kind("catalogue") != "hash":
        return report("menu_hash", False, f"catalogue is a {kind('catalogue')}, not a hash. DEL catalogue and make it with HSET.", "hash", kind("catalogue"))
    got = r.hgetall("catalogue")
    if got != want:
        return report("menu_hash", False, "The catalogue hash has different fields or prices.", json.dumps(want), json.dumps(got))
    report("menu_hash", True, "Three items, three prices, one key.")


def customer_profile():
    key = "customer:42"
    if kind(key) == "none":
        return report("customer_profile", False, f"There is no {key} yet.")
    if kind(key) != "hash":
        return report("customer_profile", False, f"{key} is a {kind(key)}, not a hash.", "hash", kind(key))
    want = {"name": "Asha", "orders": "8", "tier": "gold"}
    got = r.hgetall(key)
    if got != want:
        return report("customer_profile", False, "Asha's profile is not right yet (7 orders plus the one today).", json.dumps(want), json.dumps(got))
    report("customer_profile", True, "Asha: 8 orders, gold tier, all in one hash.")


def order_queue():
    key = "orders:pending"
    if kind(key) == "none":
        return report("order_queue", False, "There is no orders:pending list yet.")
    if kind(key) != "list":
        return report("order_queue", False, f"{key} is a {kind(key)}, not a list.", "list", kind(key))
    got = r.lrange(key, 0, -1)
    if got != ["o3", "o2"]:
        return report("order_queue", False, "The queue should still hold the two newest orders, newest first.", '["o3", "o2"]', json.dumps(got))
    report("order_queue", True, "First in, first out: o1 is being packed, o2 and o3 wait their turn.")


# ---------- chapter 5: sets and sorted sets ----------

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
    if r.smembers("customers:kothrud") != KOTHRUD or r.smembers("customers:baner") != BANER:
        return report("common_customers", False, "The store sets were changed. Press Reset lab to get them back.")
    key = "customers:both"
    if kind(key) == "none":
        return report("common_customers", False, "There is no customers:both set yet.")
    if kind(key) != "set":
        return report("common_customers", False, f"{key} is a {kind(key)}, not a set.", "set", kind(key))
    want, got = KOTHRUD & BANER, r.smembers(key)
    if got != want:
        return report("common_customers", False, "customers:both should hold exactly the people in both store sets.", ", ".join(sorted(want)), ", ".join(sorted(got)))
    report("common_customers", True, f"{len(want)} customers order from both stores.")


def top_sellers():
    want = [["mangoes", 120.0], ["rice", 80.0], ["dal", 50.0]]
    if kind("sales:today") == "none":
        return report("top_sellers", False, "There is no key named sales:today yet.")
    if kind("sales:today") != "zset":
        return report("top_sellers", False, f"sales:today is a {kind('sales:today')}, not a sorted set.", "zset", kind("sales:today"))
    got = [[m, s] for m, s in r.zrevrange("sales:today", 0, -1, withscores=True)]
    if got != want:
        return report("top_sellers", False, "The scores are not right yet (did dal get its 5 extra?).", json.dumps(want), json.dumps(got))
    report("top_sellers", True, "Best sellers, in order, kept sorted by Redis itself.")


# ---------- chapter 12: streams ----------

ORDERS = [("o1", "rice"), ("o2", "dal"), ("o3", "mangoes")]


def orders_stream():
    key = "orders:stream"
    if kind(key) == "none":
        return report("orders_stream", False, "There is no orders:stream yet.")
    if kind(key) != "stream":
        return report("orders_stream", False, f"{key} is a {kind(key)}, not a stream.", "stream", kind(key))
    got = [(f.get("order"), f.get("item")) for _, f in r.xrange(key)]
    if got != ORDERS:
        return report("orders_stream", False, "The stream should hold the three orders, oldest first, each with an order and an item field.",
                      json.dumps(ORDERS), json.dumps(got))
    report("orders_stream", True, "Three orders in the stream, in order, kept even after they are read.")


def kitchen_group():
    key = "orders:stream"
    if kind(key) != "stream":
        return report("kitchen_group", False, "Add the orders to orders:stream first.")
    groups = {g["name"]: g for g in r.xinfo_groups(key)}
    if "packing" not in groups:
        return report("kitchen_group", False, "There is no consumer group called packing on orders:stream.")
    pending = r.xpending_range(key, "packing", "-", "+", 10)
    owners = {p["consumer"] for p in pending}
    ids = [i for i, _ in r.xrange(key)]
    if [p["message_id"] for p in pending] != ids[1:] or owners != {"packer1"}:
        return report("kitchen_group", False, "packer1 should have read all three orders and acknowledged only the first.",
                      "o2 and o3 pending for packer1", f"{len(pending)} pending: {', '.join(sorted(owners)) or 'none'}")
    report("kitchen_group", True, "packer1 finished o1; o2 and o3 stay on the packing list, safe even if packer1 crashes.")


def reclaim_stuck():
    key = "payments:stream"
    if kind(key) != "stream":
        return report("reclaim_stuck", False, "payments:stream is gone. Press Reset lab to get it back.")
    if len(r.xrange(key)) != 2:
        return report("reclaim_stuck", False, "Both payments must stay in the stream; acknowledge them, do not delete them.")
    pending = r.xpending(key, "billing")["pending"]
    consumers = {c["name"] for c in r.xinfo_consumers(key, "billing")}
    if pending:
        return report("reclaim_stuck", False, f"{pending} payment(s) are still waiting for a worker that crashed.", "0 pending", f"{pending} pending")
    if "worker-2" not in consumers:
        return report("reclaim_stuck", False, "The payments were acknowledged, but never handed to worker-2. Claim them first, then acknowledge.")
    report("reclaim_stuck", True, "worker-2 took over the crashed worker's payments and finished them.")


# ---------- chapter 13: measuring Redis ----------

def slow_key_found():
    if r.get("lab:ch13:seen") is None:
        return report("slow_key_found", False, "Open chapter 13 first: its setup has not run.")
    key, cmd = r.get("answer:slow_key"), (r.get("answer:slow_command") or "").strip().upper()
    if key is None or not cmd:
        return report("slow_key_found", False, "Store what you found: the key in answer:slow_key and the command name in answer:slow_command.")
    if key in ("report:pages", "report:visitors"):
        return report("slow_key_found", False, f"{key} is in the slow log, but it is not the slowest entry. Compare the durations (the third field, in microseconds).",
                      "the slowest entry's key", key)
    if key != "report:2025":
        return report("slow_key_found", False, "That key is not the one behind the slowest entry in the slow log.", "the slowest entry's key", key)
    if cmd != "ZRANGE":
        return report("slow_key_found", False, "Right key, but the command is not the one the slow log shows for it.", "the command name in that entry", cmd)
    report("slow_key_found", True, "ZRANGE report:2025 0 -1: one command that returned 100,000 members and held up everyone else meanwhile.")


def slowlog_config():
    cfg = r.config_get("slowlog*")
    slower, length = int(cfg["slowlog-log-slower-than"]), int(cfg["slowlog-max-len"])
    if slower < 0:
        return report("slowlog_config", False, "The slow log is still switched off (a negative threshold logs nothing).", "10000", str(slower))
    if slower == 0:
        return report("slowlog_config", False, "A threshold of 0 logs every single command, which costs memory and hides the slow ones.", "10000", "0")
    if slower > 10000:
        return report("slowlog_config", False, "That threshold only catches commands slower than 10 ms; anything between is invisible.", "10000 or less", str(slower))
    if length < 1000:
        return report("slowlog_config", False, f"The slow log keeps only {length} entries, so one bad minute pushes out the evidence.", "1000 or more", str(length))
    report("slowlog_config", True, f"The slow log is on again: every command slower than {slower // 1000 or slower / 1000} ms is kept, the last {length} of them.")


# ---------- chapter 14: memory and eviction ----------

def find_big_key():
    if r.get("lab:ch10:seen") is None and r.exists("debug:log") == 0 and r.dbsize() < 1000:
        return report("find_big_key", False, "Open chapter 14 first: its incident has not started yet.")
    if r.exists("debug:log"):
        size = r.memory_usage("debug:log") or 0
        return report("find_big_key", False, f"Something huge is still eating memory ({size / 1_048_576:.0f} MB in one key).", "the debug log gone", "still there")
    if r.dbsize() < 1000 or not r.exists("cart:42"):
        return report("find_big_key", False, "Much more than the debug log is gone. Delete one key, not the whole database (Reset lab restores it).")
    report("find_big_key", True, "The runaway debug log is gone, and nothing else was touched.")


def eviction_policy():
    policy = r.config_get("maxmemory-policy")["maxmemory-policy"]
    if policy == "noeviction":
        return report("eviction_policy", False, "With noeviction, a full Redis refuses every write again.", "a policy that evicts cache entries", policy)
    if policy.startswith("allkeys"):
        return report("eviction_policy", False, f"{policy} may also evict carts, sessions and counters: data that is not a cache.",
                      "evict only keys that have a TTL", policy)
    try:
        r.set("lab:probe", "ok", ex=5)
    except redis.exceptions.ResponseError as e:
        return report("eviction_policy", False, f"Redis still refuses writes: {e}")
    report("eviction_policy", True, f"{policy}: when Redis fills up, it drops cache entries (keys with a TTL), never real data.")


# ---------- chapter 15: persistence ----------

def aof_on():
    cfg = r.config_get("append*")
    if cfg.get("appendonly") != "yes":
        return report("aof_on", False, "The append-only file is off: a restart loses everything since the last snapshot.", "appendonly yes", cfg.get("appendonly"))
    if cfg.get("appendfsync") != "everysec":
        hint = "always waits for the disk on every write" if cfg.get("appendfsync") == "always" else "leaves flushing to the operating system"
        return report("aof_on", False, f"appendfsync {cfg.get('appendfsync')} {hint}.", "everysec", cfg.get("appendfsync"))
    report("aof_on", True, "Every write is logged, and at most one second of writes can be lost.")


def fresh_snapshot():
    since = r.get("lab:ch11:since")
    if since is None:
        return report("fresh_snapshot", False, "Open chapter 15 first (its setup has not run).")
    info = r.info("persistence")
    if info.get("rdb_last_bgsave_status") != "ok":
        return report("fresh_snapshot", False, "The last snapshot failed.", "ok", info.get("rdb_last_bgsave_status"))
    if int(info.get("rdb_last_save_time", 0)) < int(since):
        return report("fresh_snapshot", False, "There is no snapshot since persistence was turned off.", "a snapshot taken now", "an old one")
    report("fresh_snapshot", True, "A fresh snapshot is on disk.")


# ---------- chapter 16: replication and clusters ----------

def replica_sync():
    try:
        r2 = redis.Redis(host="replica", decode_responses=True, socket_timeout=5)
        info = r2.info("replication")
    except Exception as e:
        return report("replica_sync", False, f"Could not reach the replica: {e}")
    if info.get("role") != "slave":
        return report("replica_sync", False, "The second server is still on its own, not a replica.", "role: replica", f"role: {info.get('role')}")
    if info.get("master_host") != "redis" or info.get("master_link_status") != "up":
        return report("replica_sync", False, "The replica is not connected to the main Redis.", "master redis, link up",
                      f"master {info.get('master_host')}, link {info.get('master_link_status')}")
    probe = f"lab:probe:{random.randint(1, 10**9)}"
    try:
        r.set(probe, "hello", ex=30)
    except redis.exceptions.ResponseError:
        return report("replica_sync", False, OOM)
    for _ in range(30):
        if r2.get(probe) == "hello":
            return report("replica_sync", True, "Writes on the main Redis appear on the replica within moments.")
        time.sleep(0.1)
    report("replica_sync", False, "A new write did not reach the replica within 3 seconds.")


def hash_tags():
    carts = [k for k in r.scan_iter(match="*customer:42*", count=1000) if k.endswith(":cart")]
    wishes = [k for k in r.scan_iter(match="*customer:42*", count=1000) if k.endswith(":wishlist")]
    if not carts or not wishes:
        return report("hash_tags", False, "Create customer 42's cart (a hash) and wishlist (a set), with key names that end in :cart and :wishlist.")
    cart, wish = carts[0], wishes[0]
    if kind(cart) != "hash" or r.hget(cart, "rice") != "2":
        return report("hash_tags", False, f"{cart} should be a hash with rice = 2.")
    if kind(wish) != "set" or not r.sismember(wish, "mangoes"):
        return report("hash_tags", False, f"{wish} should be a set containing mangoes.")
    a, b = key_slot(cart.encode()), key_slot(wish.encode())
    if a != b:
        return report("hash_tags", False, f"In a Redis Cluster, {cart} goes to slot {a} and {wish} to slot {b}: different servers, no commands across both.",
                      "the same slot", f"slots {a} and {b}")
    report("hash_tags", True, f"Both keys hash to slot {a}: a cluster keeps customer 42 together.")


# ---------- chapter 17: capstone ----------

def unlink_culprit():
    if r.get("lab:ch13:seen") is None and not r.exists("analytics:raw") and r.exists("session:s1") == 0:
        return report("unlink_culprit", False, "Open chapter 17 first: its setup has not run.")
    if r.exists("analytics:raw"):
        return report("unlink_culprit", False, "The key behind the slow log entries is still there.", "removed", "still there")
    if r.exists("session:s1") == 0 or r.exists("session:s30000") == 0:
        return report("unlink_culprit", False, "Sessions were deleted too. Only the slow key had to go (Reset lab restores them).")
    # A blocking DEL of a key that big takes milliseconds, so it lands in the slow log itself.
    for entry in r.slowlog_get(128):
        raw = entry.get("command", b"")
        cmd = (raw.decode(errors="replace") if isinstance(raw, bytes) else str(raw)).split()
        if cmd[:1] and cmd[0].upper() == "DEL" and "analytics:raw" in cmd:
            return report("unlink_culprit", False, "It is gone, but DEL froze Redis while it freed the key (the slow log caught it). "
                          "Remove it with UNLINK (Reset lab to retry).", "UNLINK", "DEL")
    report("unlink_culprit", True, "The culprit is gone, freed in the background without freezing anyone.")


# ---------- the app (chapters 6 to 11 and 17): helpers ----------

def metric(name, value, target, better="lower"):
    print("@@METRIC " + json.dumps({"name": name, "value": value, "target": target, "better": better}), flush=True)


def together(n, call):
    """n requests at the same moment: the only honest test of a race."""
    with ThreadPoolExecutor(max_workers=n) as pool:
        return list(pool.map(lambda i: call(i), range(n)))


class WrongApp(Exception):
    """The endpoint is missing: the app of another chapter is running."""


def call(task, method, path, **kw):
    resp = requests.request(method, f"{APP}{path}", timeout=kw.pop("timeout", 10), **kw)
    try:
        missing = resp.status_code == 404 and resp.json().get("detail") == "Not Found"
    except ValueError:
        missing = False
    if missing:
        raise WrongApp(f"{method} {path} does not exist in the app on port 8000: is another chapter's app running? "
                       f"Stop it (Ctrl+C) and start this one: {start_hint(task)}")
    return resp


# ---------- chapter 6: Redis from Python ----------

def profile_api():
    cid = random.randint(900_000, 999_999)
    r.hset(f"customer:{cid}", mapping={"name": "Zoya", "orders": "12", "tier": "silver"})
    try:
        got = call("profile_api", "GET", f"/customers/{cid}")
        missing = call("profile_api", "GET", f"/customers/{cid + 1}")
    finally:
        r.delete(f"customer:{cid}")
    want = {"id": cid, "name": "Zoya", "orders": 12, "tier": "silver"}
    if got.status_code != 200:
        return report("profile_api", False, f"GET /customers/{cid} answered {got.status_code}.", "200", f"{got.status_code} {got.text[:120]}")
    if got.json() != want:
        return report("profile_api", False, "The profile is not right (orders must be a number, not text).", json.dumps(want), json.dumps(got.json()))
    if missing.status_code != 404:
        return report("profile_api", False, "A customer that does not exist must get a 404.", "404", str(missing.status_code))
    report("profile_api", True, "Profiles come straight from the hash, with the right types.")


def bulk_import():
    r.delete("sales:import")
    reads = lambda: int(r.info("stats")["total_reads_processed"])
    before = reads()
    t0 = time.monotonic()
    resp = call("bulk_import", "POST", "/import", timeout=60)
    ms = (time.monotonic() - t0) * 1000
    trips = reads() - before - 1  # minus our own INFO
    metric("round_trips", trips, 100)
    if resp.status_code != 200:
        return report("bulk_import", False, f"POST /import answered {resp.status_code}.", "200", f"{resp.status_code} {resp.text[:120]}")
    if r.hlen("sales:import") != 2000 or r.hget("sales:import", "store01:rice") != "79":
        return report("bulk_import", False, "sales:import does not hold the 2000 rows of data/sales.csv.", "2000 fields", f"{r.hlen('sales:import')} fields")
    if trips > 100:
        return report("bulk_import", False, f"The import made about {trips} round trips to Redis. At 0.5 ms each in production, that is {trips * 0.5 / 1000:.1f} s.",
                      "a handful of round trips", f"about {trips}")
    report("bulk_import", True, f"2000 rows in {max(trips, 1)} round trip(s), {ms:.0f} ms.")


# ---------- chapter 7: caching ----------

def price_cache():
    item, key = "atta", "price:atta"
    r.delete(key)  # start cold, so the first call must go to the catalogue
    t0 = time.monotonic()
    first = call("price_cache", "GET", f"/price/{item}")
    cold = time.monotonic() - t0
    t0 = time.monotonic()
    second = call("price_cache", "GET", f"/price/{item}")
    warm = time.monotonic() - t0
    want = {"item": item, "price": 55}
    for resp in (first, second):
        if resp.status_code != 200 or resp.json() != want:
            return report("price_cache", False, f"/price/{item} gave the wrong answer.", json.dumps(want), f"{resp.status_code} {resp.text[:200]}")
    if warm > 0.3:
        return report("price_cache", False, f"The second call still took {warm:.2f} s, so nothing was read from Redis.", "< 0.3 s", f"{warm:.2f} s")
    if cold < 1.0:
        return report("price_cache", False, "The first call was fast even with an empty cache. Ask the catalogue on a miss.")
    ttl = r.ttl(key)
    if ttl == -2:
        return report("price_cache", False, f"Nothing was stored under {key}.", key, "missing")
    if ttl == -1 or ttl > 60:
        return report("price_cache", False, f"{key} must expire within 60 seconds, so price changes show up.", "<= 60 s", "no expiry" if ttl == -1 else f"{ttl} s")
    report("price_cache", True, f"First call {cold:.2f} s, second {warm * 1000:.0f} ms: about {cold / max(warm, 0.0005):,.0f} times faster.")


def price_invalidate():
    item = "bread"
    try:
        call("price_invalidate", "GET", f"/price/{item}")  # warm the cache with 45
        call("price_invalidate", "PUT", f"/price/{item}", json={"price": 50})
        after = call("price_invalidate", "GET", f"/price/{item}")
        t0 = time.monotonic()
        again = call("price_invalidate", "GET", f"/price/{item}")  # must come from the cache again
        again_s = time.monotonic() - t0
    finally:
        requests.put(f"{APP}/price/{item}", json={"price": 45}, timeout=10)
        r.delete(f"price:{item}")
    got = after.json().get("price") if after.status_code == 200 else after.status_code
    if got != 50:
        return report("price_invalidate", False, "After a price change, the next read still shows the old price from Redis.", "50", str(got))
    if again_s > 0.3 or again.json().get("price") != 50:
        return report("price_invalidate", False, "Prices are not cached at all, so nothing can be stale. Do the cache task first.", "a cached read after the change", f"{again_s:.2f} s")
    report("price_invalidate", True, "A price change shows up on the very next read, and the read after that is fast again.")


# ---------- chapter 8: what the cache saves ----------

def ten_reads(task):
    """One miss, then nine hits, on counters that start at zero."""
    item = "onions"
    r.delete("price:onions", "stats:price:hits", "stats:price:misses")
    for _ in range(10):
        resp = call(task, "GET", f"/price/{item}")
        if resp.status_code != 200 or resp.json().get("price") != 40:
            raise AssertionError(f"/price/{item} answered {resp.status_code} {resp.text[:120]}")


def hit_counter():
    try:
        ten_reads("hit_counter")
    except AssertionError as e:
        return report("hit_counter", False, str(e))
    hits, misses = r.get("stats:price:hits"), r.get("stats:price:misses")
    if hits is None and misses is None:
        return report("hit_counter", False, "Ten reads of /price/onions (one miss, nine hits) counted nothing in Redis.",
                      "stats:price:hits 9, stats:price:misses 1", "no counters")
    if (hits, misses) == ("1", "9"):
        return report("hit_counter", False, "The counters are the wrong way round: the first read is the miss, the other nine are hits.", "9 hits, 1 miss", "1 hit, 9 misses")
    if (hits, misses) != ("9", "1"):
        return report("hit_counter", False, "Ten reads (one miss, then nine hits) gave different counts.", "9 hits, 1 miss", f"{hits} hits, {misses} misses")
    report("hit_counter", True, "Nine hits, one miss: a 90% hit rate, counted by Redis at almost no cost.")


def savings_report():
    try:
        ten_reads("savings_report")
    except AssertionError as e:
        return report("savings_report", False, str(e))
    resp = call("savings_report", "GET", "/savings")
    if resp.status_code != 200:
        return report("savings_report", False, f"GET /savings answered {resp.status_code}.", "200", f"{resp.status_code} {resp.text[:120]}")
    got = resp.json()
    want = {"hits": 9, "misses": 1, "hit_rate": 0.9, "seconds_saved": 13.5, "rupees_saved": 0.9}
    for field, value in want.items():
        if field not in got:
            return report("savings_report", False, f"/savings has no {field} field.", json.dumps(want), json.dumps(got))
        if not isinstance(got[field], (int, float)) or abs(got[field] - value) > 0.001:
            return report("savings_report", False, f"After one miss and nine hits, {field} is wrong.", str(value), json.dumps(got[field]))
    r.delete("stats:price:hits", "stats:price:misses")
    empty = call("savings_report", "GET", "/savings")
    if empty.status_code != 200 or empty.json().get("hit_rate") != 0:
        return report("savings_report", False, "With no reads yet, /savings must answer a hit_rate of 0, not an error.", "hit_rate 0",
                      f"{empty.status_code} {empty.text[:120]}")
    report("savings_report", True, "Nine hits saved 13.5 seconds of waiting and Rs 0.90. At a million reads a day, that is real money.")


# ---------- chapter 9: the stampede ----------

def stampede_lock():
    item = "paneer"
    r.delete(f"price:{item}", f"lock:price:{item}")
    before = int(r.get("catalogue:calls") or 0)
    answers = together(30, lambda i: call("stampede_lock", "GET", f"/price/{item}", timeout=15))
    calls = int(r.get("catalogue:calls") or 0) - before
    metric("catalogue_calls", calls, 2)
    bad = [a for a in answers if a.status_code != 200 or a.json().get("price") != 90]
    if bad:
        return report("stampede_lock", False, f"{len(bad)} of 30 requests did not get the price.", "200 and 90 for all 30", f"{bad[0].status_code} {bad[0].text[:100]}")
    if calls > 2:
        return report("stampede_lock", False, f"30 requests at once on an empty cache made {calls} calls to the slow catalogue.", "1 (at most 2)", str(calls))
    report("stampede_lock", True, f"30 requests at once, {calls} call to the catalogue. The stampede is over.")


def jitter_ttl():
    items = ["rice", "dal", "mangoes", "eggs", "atta", "onions"]
    r.delete(*[f"price:{i}" for i in items])
    answers = together(len(items), lambda i: call("jitter_ttl", "GET", f"/price/{items[i]}", timeout=15))
    if any(a.status_code != 200 for a in answers):
        return report("jitter_ttl", False, "Not every price came back.", "200 for all six", str(sorted({a.status_code for a in answers})))
    ttls = [r.ttl(f"price:{i}") for i in items]
    if any(t < 0 for t in ttls):
        return report("jitter_ttl", False, "Some prices were stored without a lifetime.", "45 to 60 s each", str(ttls))
    if any(t > 60 or t < 40 for t in ttls):
        return report("jitter_ttl", False, "Each lifetime should be between 45 and 60 seconds.", "45 to 60 s", str(ttls))
    if len(set(ttls)) == 1:
        return report("jitter_ttl", False, f"Six prices cached at the same moment all expire after {ttls[0]} s, so they also expire together.",
                      "different lifetimes", str(ttls))
    report("jitter_ttl", True, f"Six prices cached together now expire at different moments ({', '.join(map(str, ttls))} s).")


# ---------- chapter 10: atomic operations ----------

def otp_limit():
    phone = "9000000001"
    key = f"otp:count:{phone}"
    r.delete(key)
    try:
        codes = [call("otp_limit", "POST", f"/otp/{phone}").status_code for _ in range(4)]
    finally:
        ttl = r.ttl(key)
        r.delete(key)
    if codes != [200, 200, 200, 429]:
        return report("otp_limit", False, "Four login codes in a row should give three 200s, then a 429.", "[200, 200, 200, 429]", str(codes))
    if ttl == -2:
        return report("otp_limit", False, f"The count must live in Redis under {key}.", key, "missing")
    if ttl == -1 or ttl > 60:
        return report("otp_limit", False, f"{key} must expire within a minute, or the phone is blocked forever.", "<= 60 s", "no expiry" if ttl == -1 else f"{ttl} s")
    report("otp_limit", True, "Three codes go through, the fourth gets a 429, and the count resets within a minute.")


def redeem_points():
    cid = random.randint(900_000, 999_999)
    key = f"coins:{cid}"
    r.set(key, 500)
    try:
        codes = [a.status_code for a in together(20, lambda i: call("redeem_points", "POST", f"/redeem/{cid}?coins=100"))]
        left = r.get(key)
    finally:
        r.delete(key)
    ok = codes.count(200)
    if ok != 5 or left != "0":
        return report("redeem_points", False, f"500 coins, 20 redemptions of 100 at once: {ok} went through and {left} coins are left.",
                      "exactly 5 through, 0 left", f"{ok} through, {left} left")
    if codes.count(409) != 15:
        return report("redeem_points", False, "The 15 that cannot be paid must get a 409.", "15 x 409", str(sorted(set(codes))))
    report("redeem_points", True, "20 redemptions at once: exactly 5 paid, and the balance never went below zero.")


# ---------- chapter 11: locks ----------

def book_once():
    slot = random.randint(900_000, 999_999)
    key = f"booking:slot:{slot}"
    try:
        answers = together(30, lambda i: call("book_once", "POST", f"/book/{slot}?customer=c{i}"))
        winner = r.get(key)
    finally:
        r.delete(key)
    wins = [a for a in answers if a.status_code == 200]
    if len(wins) != 1:
        return report("book_once", False, f"30 customers booked slot {slot} at the same moment and {len(wins)} were told it is theirs.", "exactly 1", str(len(wins)))
    if winner != wins[0].json().get("booked_for"):
        return report("book_once", False, "The slot is stored for someone other than the customer told they won.", wins[0].json().get("booked_for"), str(winner))
    if any(a.status_code not in (200, 409) for a in answers):
        return report("book_once", False, "Everyone else must get a 409.", "409", str(sorted({a.status_code for a in answers})))
    report("book_once", True, "30 at once, exactly one booking, everyone else told politely.")


def safe_unlock():
    name = f"report-{random.randint(900_000, 999_999)}"
    key = f"lock:{name}"
    r.set(key, "token-A", ex=30)
    try:
        call("safe_unlock", "POST", f"/locks/{name}/release", json={"token": "token-B"})
        stolen = r.get(key) != "token-A"
        call("safe_unlock", "POST", f"/locks/{name}/release", json={"token": "token-A"})
        still = r.exists(key)
    finally:
        r.delete(key)
    if stolen:
        return report("safe_unlock", False, "Releasing with token-B removed a lock that token-A holds.", "the lock stays with token-A", "the lock is gone")
    if still:
        return report("safe_unlock", False, "The real owner (token-A) could not release its own lock.", "the lock released", "the lock is still there")
    report("safe_unlock", True, "Only the owner can release the lock.")


# ---------- chapter 17: capstone ----------

def scan_not_keys():
    stats = lambda: r.info("commandstats")
    calls = lambda st, c: st.get(f"cmdstat_{c}", {}).get("calls", 0)
    before = stats()
    resp = call("scan_not_keys", "GET", "/sessions/active", timeout=20)
    after = stats()
    if resp.status_code != 200:
        return report("scan_not_keys", False, f"GET /sessions/active answered {resp.status_code}.", "200", resp.text[:120])
    want = sum(1 for _ in r.scan_iter(match="session:*", count=1000))
    if calls(after, "keys") > calls(before, "keys"):
        return report("scan_not_keys", False, "The endpoint still uses KEYS, which blocks Redis for every other client while it walks all keys.", "SCAN", "KEYS")
    if calls(after, "scan") <= calls(before, "scan"):
        return report("scan_not_keys", False, "The endpoint did not use SCAN.", "SCAN", "something else")
    if resp.json().get("active") != want:
        return report("scan_not_keys", False, "The count of active sessions is wrong.", str(want), str(resp.json().get("active")))
    report("scan_not_keys", True, f"{want} sessions counted with SCAN, in small steps, without blocking anyone.")


REDIS_TASKS = [measure_latency, measure_redis, first_keys, cups_counter, clean_up, otp_expiry, session_ttl, keep_forever,
               menu_hash, customer_profile, order_queue, unique_visitors, common_customers, top_sellers, orders_stream,
               kitchen_group, reclaim_stuck, slow_key_found, slowlog_config, find_big_key, eviction_policy, aof_on,
               fresh_snapshot, replica_sync, hash_tags, unlink_culprit]
APP_TASKS = [profile_api, bulk_import, price_cache, price_invalidate, hit_counter, savings_report, stampede_lock, jitter_ttl,
             otp_limit, redeem_points, book_once, safe_unlock, scan_not_keys]


def app_up():
    try:
        requests.get(f"{APP}/docs", timeout=3)
        return True
    except requests.RequestException:
        return False


def guarded(check):
    """A Redis that refuses writes (the chapter 14 incident) must not break every other check."""
    try:
        check()
    except redis.exceptions.ResponseError as e:
        report(check.__name__, False, OOM if "OOM" in str(e) else f"Redis answered an error: {e}")
    except WrongApp as e:
        report(check.__name__, False, str(e))
    except requests.RequestException as e:
        report(check.__name__, False, f"Calling your app failed: {e}")


for check in REDIS_TASKS:
    if not WANTED or check.__name__ in WANTED:
        guarded(check)
wanted_app = [c for c in APP_TASKS if not WANTED or c.__name__ in WANTED]
if wanted_app:
    if app_up():
        for check in wanted_app:
            guarded(check)
    else:
        for check in wanted_app:
            report(check.__name__, False, f"Your app is not answering on port 8000. Start this chapter's app in a terminal: {start_hint(check.__name__)}")
