"""State the backend's workers share (Phase H2): locks on lab machines, the one-check-per-learner slot,
AI request counters and the reaper's leader lease.

With REDIS_URL set it lives in Redis, so uvicorn can run several workers (and later several servers).
Without it, it lives in this process's memory, exactly as before: then run one worker.
Every key starts with "labbox:".
"""
import logging
import secrets
import threading
import time
from collections import defaultdict, deque
from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache

from .config import get_settings

log = logging.getLogger(__name__)

PREFIX = "labbox:"
# A machine lock is held while a container starts or stops (a minute at worst). If its worker dies, the
# lock frees itself after this long; a live holder renews it in the background.
LOCK_SECONDS = 60
LOCK_WAIT_SECONDS = 300


class Busy(Exception):
    """A lock could not be taken in time."""


# ---------- the store ----------


@lru_cache
def redis_client():
    import redis

    url = get_settings().REDIS_URL
    return redis.Redis.from_url(url, socket_timeout=5, socket_connect_timeout=5, health_check_interval=30) if url else None


def backend() -> str:
    return "redis" if get_settings().REDIS_URL else "memory"


_mem_locks: defaultdict[str, threading.Lock] = defaultdict(threading.Lock)
_mem_guard = threading.Lock()
_mem_claims: dict[str, tuple[str, float]] = {}  # key -> (token, expires at)
_mem_hits: defaultdict[str, deque[float]] = defaultdict(deque)


# ---------- locks: one holder at a time, waits for its turn ----------


@contextmanager
def lock(name: str, wait: float = LOCK_WAIT_SECONDS) -> Iterator[None]:
    """Hold `name` for the block (for example a lab machine while it starts). Blocks until free."""
    r = redis_client()
    if r is None:
        m = _mem_locks[name]
        if not m.acquire(timeout=wait):
            raise Busy(name)
        try:
            yield
        finally:
            m.release()
        return
    held = r.lock(PREFIX + "lock:" + name, timeout=LOCK_SECONDS, blocking_timeout=wait, thread_local=False)
    if not held.acquire():
        raise Busy(name)
    stop = threading.Event()

    def renew() -> None:  # keep the lease while the work runs, so a slow start never loses it
        while not stop.wait(LOCK_SECONDS / 3):
            try:
                held.reacquire()
            except Exception:
                log.warning("Could not renew lock %s", name)
                return

    t = threading.Thread(target=renew, daemon=True)
    t.start()
    try:
        yield
    finally:
        stop.set()
        try:
            held.release()
        except Exception:  # it expired (worker paused for a minute): nothing left to release
            log.warning("Lock %s had already expired", name)


# ---------- claims: take it now or get told it is taken ----------


def claim(key: str, seconds: float) -> str | None:
    """Take `key` for at most `seconds` without waiting. A token to release it with, or None if taken."""
    token = secrets.token_hex(8)
    r = redis_client()
    if r is None:
        now = time.monotonic()
        with _mem_guard:
            held = _mem_claims.get(key)
            if held and held[1] > now:
                return None
            _mem_claims[key] = (token, now + seconds)
        return token
    return token if r.set(PREFIX + key, token, nx=True, px=int(seconds * 1000)) else None


_RELEASE = "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end"


def release(key: str, token: str) -> None:
    """Give `key` back, only if it is still ours (it may have expired and been taken by someone else)."""
    r = redis_client()
    if r is None:
        with _mem_guard:
            if _mem_claims.get(key, ("",))[0] == token:
                del _mem_claims[key]
        return
    r.eval(_RELEASE, 1, PREFIX + key, token)


def keep(key: str, token: str, seconds: float) -> bool:
    """Take `key` if free, or extend it if it is already ours (a leader lease). True if ours now."""
    r = redis_client()
    if r is None:
        now = time.monotonic()
        with _mem_guard:
            held = _mem_claims.get(key)
            if held and held[1] > now and held[0] != token:
                return False
            _mem_claims[key] = (token, now + seconds)
        return True
    k = PREFIX + key
    if r.set(k, token, nx=True, px=int(seconds * 1000)):
        return True
    return bool(r.eval(
        "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('pexpire', KEYS[1], ARGV[2]) else return 0 end",
        1, k, token, int(seconds * 1000),
    ))


# ---------- counters: requests in the last N seconds ----------


def recent(key: str, window: float = 60) -> int:
    """How many hits `key` had in the last `window` seconds."""
    r = redis_client()
    now = time.time()
    if r is None:
        with _mem_guard:
            hits = _mem_hits[key]
            while hits and now - hits[0] > window:
                hits.popleft()
            return len(hits)
    k = PREFIX + "hits:" + key
    p = r.pipeline()
    p.zremrangebyscore(k, 0, now - window)
    p.zcard(k)
    return int(p.execute()[1])


def hit(key: str, window: float = 60) -> None:
    """Count one hit for `key` now."""
    r = redis_client()
    now = time.time()
    if r is None:
        with _mem_guard:
            _mem_hits[key].append(now)
        return
    k = PREFIX + "hits:" + key
    p = r.pipeline()
    p.zadd(k, {f"{now}:{secrets.token_hex(4)}": now})
    p.expire(k, int(window) + 1)
    p.execute()


# ---------- small values with an expiry (why a machine stopped, CPU samples) ----------

_mem_values: dict[str, tuple[str, float]] = {}  # key -> (value, expires at, monotonic)


def put(key: str, value: str, seconds: float) -> None:
    r = redis_client()
    if r is None:
        with _mem_guard:
            _mem_values[key] = (value, time.monotonic() + seconds)
        return
    r.set(PREFIX + "val:" + key, value, px=int(seconds * 1000))


def get(key: str) -> str | None:
    r = redis_client()
    if r is None:
        with _mem_guard:
            held = _mem_values.get(key)
            if held and held[1] > time.monotonic():
                return held[0]
            _mem_values.pop(key, None)
            return None
    raw = r.get(PREFIX + "val:" + key)
    return raw.decode() if isinstance(raw, bytes) else raw


def delete(key: str) -> None:
    r = redis_client()
    if r is None:
        with _mem_guard:
            _mem_values.pop(key, None)
        return
    r.delete(PREFIX + "val:" + key)


def forget_hits() -> None:
    """Tests only: start every counter from zero."""
    r = redis_client()
    with _mem_guard:
        _mem_hits.clear()
    if r is not None:
        for k in r.scan_iter(PREFIX + "hits:*"):
            r.delete(k)


def ping() -> bool:
    r = redis_client()
    if r is None:
        return True
    try:
        return bool(r.ping())
    except Exception:
        return False
