import threading

import httpx
import r

POLICY = "DS-POL-40000"


def serve(busy_every):
    import policy_service
    server = policy_service.make_server(port=8081, busy_every=busy_every)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


class Client:
    """Answers with a list of status codes in turn, and counts the calls."""
    def __init__(self, codes, body):
        self.codes, self.body, self.calls = list(codes), body, 0

    def get(self, url, timeout=None):
        self.calls += 1
        code = self.codes.pop(0)
        return httpx.Response(code, text=self.body if code == 200 else "<error>busy</error>", request=httpx.Request("GET", url))


def test_fetch_policy():
    def check():
        import legacy
        server = serve(busy_every=0)
        try:
            got = legacy.fetch_policy(POLICY)
        finally:
            server.shutdown()
            server.server_close()
        want = {"policy_no": "DS-POL-40000", "holder": "M. Joshi", "vehicle_reg": "MH12EB4010", "vehicle": "two-wheeler",
                "start_date": "2026-04-27", "end_date": "2027-04-26", "sum_insured": 90000, "deductible": 1000}
        if got != want:
            if isinstance(got, dict) and "number" in got:
                return r.failed("fetch_policy", "The old system calls it <number>, <start> and <end>; Claimdesk uses policy_no, start_date and "
                                "end_date. Use TAGS.get(child.tag, child.tag) as the key.", want, got)
            if isinstance(got, dict) and got.get("sum_insured") == "90000":
                return r.failed("fetch_policy", "XML text is always a string: turn the tags in NUMBERS (sum_insured, deductible) into int.",
                                want, got)
            return r.failed("fetch_policy", "Parse the XML with ET.fromstring and make one key per child element.", want, got)
        r.passed("fetch_policy", "The old system's names stay at the edge: everything after this function speaks Claimdesk's names.")
    r.task("fetch_policy", check)


def test_retry_busy():
    def check():
        import legacy
        xml = '<policy><number>DS-POL-1</number><holder>X</holder><sum_insured>5</sum_insured><deductible>1</deductible></policy>'
        waits = []
        real_sleep = legacy.time.sleep
        legacy.time.sleep = waits.append
        try:
            c = Client([503, 503, 200], xml)
            got = legacy.fetch_with_retry("DS-POL-1", attempts=3, wait=0.2, client=c)
            if c.calls != 3 or not isinstance(got, dict) or got.get("policy_no") != "DS-POL-1":
                return r.failed("retry_busy", "Busy, busy, then the answer: fetch_with_retry should try three times and return the policy.",
                                "3 calls and the policy", f"{c.calls} calls, {got!r}")
            if [round(w, 3) for w in waits] != [0.2, 0.4]:
                return r.failed("retry_busy", "Wait longer each time: wait * 2 ** try_number gives 0.2 then 0.4 seconds.", [0.2, 0.4], waits)
            waits.clear()
            c = Client([503, 503, 503], xml)
            try:
                legacy.fetch_with_retry("DS-POL-1", attempts=3, wait=0.2, client=c)
                return r.failed("retry_busy", "Busy three times: after the last try, raise the error so the caller knows it failed.",
                                "HTTPStatusError", "a return value")
            except httpx.HTTPStatusError:
                pass
            if c.calls != 3 or len(waits) != 2:
                return r.failed("retry_busy", "Three tries means two waits, and no wait after the last try.", "3 calls, 2 waits",
                                f"{c.calls} calls, {len(waits)} waits")
            c = Client([500, 200], xml)
            try:
                legacy.fetch_with_retry("DS-POL-1", attempts=3, wait=0.2, client=c)
                return r.failed("retry_busy", "A 500 is a real error, not \"busy\": raise it at once, retry only 503.", "HTTPStatusError", "retried")
            except httpx.HTTPStatusError:
                pass
            c = Client([404], xml)
            try:
                legacy.fetch_with_retry("DS-POL-404", attempts=3, wait=0.2, client=c)
            except LookupError:
                pass
            if c.calls != 1:
                return r.failed("retry_busy", "A policy that does not exist will not appear on a retry: LookupError should pass straight through.",
                                1, c.calls)
        finally:
            legacy.time.sleep = real_sleep
        r.passed("retry_busy", "Busy is temporary, so you wait a little longer each time; missing and broken are not, so you stop.")
    r.task("retry_busy", check)
