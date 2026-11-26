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
    # TODO (task classify_email): look in the subject and body together, lower-cased. In this order:
    # "photo" -> "photos"; "status", "update" or "where is" -> "status"; "new claim" -> "new_claim";
    # "attach", "rc", "invoice", "estimate", "pan" -> "documents"; "complaint", "escalat", "unhappy", "disappointed",
    # "poor service" -> "complaint"; anything else -> "other".
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
    # TODO (task costliest_kind): use minutes_by_kind. Return (kind, share), share = its minutes / all minutes * 100,
    # rounded to 1 decimal place.
    return ("", 0.0)


if __name__ == "__main__":
    emails = load_inbox()
    counts = Counter(classify(e) for e in emails)
    minutes = minutes_by_kind(emails)
    print("kind        emails  minutes")
    for kind in KINDS + ["other"]:
        print(f"{kind:<11} {counts.get(kind, 0):>6}  {minutes.get(kind, 0):>7}")
    print("costliest:", costliest(emails))
