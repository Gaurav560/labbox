"""Claimdesk asks Deccan Shield's old policy system for a policy. It answers XML, and when it is busy it says 503.
Start the system in a second terminal (python policy_service.py), then run: python legacy.py"""
import time
import xml.etree.ElementTree as ET

import httpx

BASE = "http://127.0.0.1:8081"
NUMBERS = ["sum_insured", "deductible"]  # these tags hold whole rupees
TAGS = {"number": "policy_no", "start": "start_date", "end": "end_date"}  # the old system's names -> ours


def parse_policy(xml_text):
    """The <policy> XML as a dict with our names (TAGS), sum_insured and deductible as ints, the rest as strings."""
    # TODO (task fetch_policy): ET.fromstring(xml_text) gives the <policy> element. For each child, the key is
    # TAGS.get(child.tag, child.tag) and the value child.text; the tags in NUMBERS become int.
    return {}


def fetch_policy(number, client=httpx):
    """GET /policy/<number> and return the parsed policy. 404 raises LookupError; other errors raise HTTPStatusError."""
    response = client.get(f"{BASE}/policy/{number}", timeout=5)
    if response.status_code == 404:
        raise LookupError(f"no policy {number}")
    response.raise_for_status()
    return parse_policy(response.text)


def fetch_with_retry(number, attempts=3, wait=0.2, client=httpx):
    """fetch_policy, tried again when the system answers 503 (busy): at most `attempts` tries, waiting `wait` seconds
    before the second try and twice as long before each later one. Any other error, or 503 on the last try, is raised."""
    # TODO (task retry_busy): loop over the tries. Catch httpx.HTTPStatusError; if its response.status_code is 503 and
    # this is not the last try, time.sleep(wait * 2 ** try_number) and go round again; otherwise raise it.
    return fetch_policy(number, client)


if __name__ == "__main__":
    for number in ["DS-POL-40000", "DS-POL-40037", "DS-POL-40074", "DS-POL-40111"]:
        try:
            print(fetch_with_retry(number))
        except httpx.HTTPStatusError as e:
            print(number, "failed:", e.response.status_code, e.response.text.strip())
