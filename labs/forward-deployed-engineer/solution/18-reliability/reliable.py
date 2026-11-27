"""Reliability: pace the calls, remember answers, and never lose an email. Run it with: python reliable.py"""
import hashlib
import json
import time

from extract import client, load_emails, safe_extract

PROMPT_VERSION = "v1"  # change it whenever SYSTEM, the schema or the model changes: old answers then stop counting


def cache_key(text, version=PROMPT_VERSION):
    """The same email read with the same prompt version always has the same key."""
    return hashlib.sha256(f"{version}\n{text}".encode()).hexdigest()


class Pacer:
    """Keeps calls at least 60 / per_minute seconds apart, so a batch stays under a rate limit."""

    def __init__(self, per_minute, clock=time.monotonic, sleep=time.sleep):
        self.gap = 60 / per_minute
        self.clock = clock
        self.sleep = sleep
        self.last = None

    def wait(self):
        """Call just before each model call: sleeps if the previous call was less than gap seconds ago."""
        now = self.clock()
        if self.last is not None and now - self.last < self.gap:
            self.sleep(self.gap - (now - self.last))
            now = self.clock()
        self.last = now


def cached_extract(text, cache, extract=safe_extract, version=PROMPT_VERSION):
    """(fields as a dict, problem, called). From the cache when this text was read before with this prompt version,
    without a call; otherwise extract(text) once. Only successful reads are stored: a failure is tried again next time."""
    key = cache_key(text, version)
    if key in cache:
        return cache[key], None, False
    fields, problem = extract(text)
    if problem is not None:
        return None, problem, True
    cache[key] = fields.model_dump()
    return cache[key], None, True


def load_cache(path="cache.json"):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_cache(cache, path="cache.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cache, f)


def run_batch(emails, cache, pacer, openai):
    """Reads every email: from the cache when it can, otherwise from the model, paced. Returns (calls, failed)."""
    def paced(text):
        pacer.wait()
        return safe_extract(text, openai)

    calls, failed = 0, []
    for email in emails:
        _, problem, called = cached_extract(email["text"], cache, paced)
        calls += called
        if problem:
            failed.append((email["email_id"], problem))
    return calls, failed


if __name__ == "__main__":
    cache = load_cache()
    openai = client()
    for label in ("first run", "second run"):
        start = time.monotonic()
        calls, failed = run_batch(load_emails(), cache, Pacer(19), openai)
        save_cache(cache)
        print(f"{label}: {calls} model calls, {len(failed)} failed, {time.monotonic() - start:.0f} s {failed}")
