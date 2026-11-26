"""Discovery: 40 emails from the claims inbox, with the minutes an adjuster spent on each. What eats the time?
Run it with: python discovery.py"""
import csv
from collections import Counter

KINDS = ["photos", "status", "new_claim", "documents", "complaint"]


def load_inbox(path="data/inbox_sample.csv"):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def classify(email):
    """One of KINDS, or "other": what this email is about, from its subject and body."""
    text = (email["subject"] + " " + email["body"]).lower()
    if "photo" in text:
        return "photos"
    if "status" in text or "update" in text or "where is" in text:
        return "status"
    if "new claim" in text:
        return "new_claim"
    if any(w in text for w in ("attach", "rc", "invoice", "estimate", "pan")):
        return "documents"
    if any(w in text for w in ("complaint", "escalat", "unhappy", "disappointed", "poor service")):
        return "complaint"
    return "other"


def minutes_by_kind(emails):
    """Total adjuster minutes per kind, as a dict."""
    total = {}
    for e in emails:
        kind = classify(e)
        total[kind] = total.get(kind, 0) + int(e["minutes"])
    return total


def costliest(emails):
    """The kind that costs the most adjuster minutes, and its share of all minutes in percent (1 decimal)."""
    minutes = minutes_by_kind(emails)
    kind = max(minutes, key=minutes.get)
    return (kind, round(minutes[kind] / sum(minutes.values()) * 100, 1))


if __name__ == "__main__":
    emails = load_inbox()
    counts = Counter(classify(e) for e in emails)
    minutes = minutes_by_kind(emails)
    print("kind        emails  minutes")
    for kind in KINDS + ["other"]:
        print(f"{kind:<11} {counts.get(kind, 0):>6}  {minutes.get(kind, 0):>7}")
    print("costliest:", costliest(emails))
