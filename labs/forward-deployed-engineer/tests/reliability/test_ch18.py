import r


class Clock:
    def __init__(self):
        self.t = 100.0
        self.slept = []

    def now(self):
        return self.t

    def sleep(self, s):
        self.slept.append(round(s, 3))
        self.t += s


def test_pacer():
    def check():
        from reliable import Pacer
        c = Clock()
        p = Pacer(20, clock=c.now, sleep=c.sleep)
        p.wait()
        if c.slept:
            return r.failed("pacer", "The first call never waits.", [], c.slept)
        c.t += 1.0
        p.wait()
        if c.slept != [2.0]:
            return r.failed("pacer", "20 a minute is one call every 3 seconds: 1 second after a call, wait the other 2.", [2.0], c.slept)
        c.t += 5.0
        p.wait()
        if c.slept != [2.0]:
            return r.failed("pacer", "5 seconds after the last call, no wait is needed.", [2.0], c.slept)
        p.wait()
        if c.slept != [2.0, 3.0]:
            return r.failed("pacer", "Right after a call, wait the whole gap. Remember the time AFTER sleeping as last.", [2.0, 3.0], c.slept)
        c.t += 0.5
        p.wait()
        if c.slept != [2.0, 3.0, 2.5]:
            return r.failed("pacer", "Measure from the moment the previous call really started (after its sleep).", [2.0, 3.0, 2.5], c.slept)
        r.passed("pacer", "A batch of 30 now takes about 95 seconds and never hits the 20-a-minute limit.")
    r.task("pacer", check)


class Fields:
    def __init__(self, d):
        self.d = d

    def model_dump(self):
        return dict(self.d)


def test_cache():
    def check():
        from reliable import cache_key, cached_extract
        calls = []

        def ok(text):
            calls.append(text)
            return Fields({"policy_no": "DS-POL-40000", "text_len": len(text)}), None

        cache = {}
        got = cached_extract("email one", cache, ok)
        if got != ({"policy_no": "DS-POL-40000", "text_len": 9}, None, True) or len(calls) != 1:
            return r.failed("cache", "A new email: call extract once and return (fields.model_dump(), None, True).",
                            ({"policy_no": "DS-POL-40000", "text_len": 9}, None, True), got)
        if cache.get(cache_key("email one")) != {"policy_no": "DS-POL-40000", "text_len": 9}:
            return r.failed("cache", "Store the fields as a dict under cache_key(text, version).")
        got = cached_extract("email one", cache, ok)
        if len(calls) != 1 or got != ({"policy_no": "DS-POL-40000", "text_len": 9}, None, False):
            return r.failed("cache", "The same email again must come from the cache: no call, and called is False.",
                            "1 call in total", f"{len(calls)} calls")
        cached_extract("email one", cache, ok, version="v2")
        if len(calls) != 2:
            return r.failed("cache", "A new prompt version must not reuse old answers: the key includes the version.")

        def broken(text):
            calls.append(text)
            return None, "the model call failed: RateLimitError"

        got = cached_extract("email two", cache, broken)
        if got != (None, "the model call failed: RateLimitError", True):
            return r.failed("cache", "A failed read returns (None, problem, True).", (None, "the model call failed: RateLimitError", True), got)
        n = len(calls)
        cached_extract("email two", cache, broken)
        if len(calls) != n + 1:
            return r.failed("cache", "Never store a failure: the next run must try that email again.")
        r.passed("cache", "A rerun costs nothing for emails already read, and failures get another chance.")
    r.task("cache", check)
