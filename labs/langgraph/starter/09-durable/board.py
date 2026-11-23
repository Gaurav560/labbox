"""The board's other systems, pretend versions that write what they did to board_record.txt.

A real crew booking or parts order costs money if it happens twice, so the record shows every action.
SMS_FAILS=<n> makes the SMS gateway time out on its first n attempts in this process.
"""
import os
from pathlib import Path

RECORD = Path("board_record.txt")
ATTEMPTS = {"sms": 0}


class SmsTimeout(Exception):
    """The SMS gateway did not answer in time."""


def _record(line: str) -> str:
    with RECORD.open("a") as f:
        f.write(line + "\n")
    return line


def book_crew(job: str) -> str:
    return _record(f"{job}: crew booked (South zone, tomorrow 8:00)")


def order_parts(job: str) -> str:
    return _record(f"{job}: parts ordered, Rs 18,000 (200 mm valve, 2 couplings)")


def send_sms(job: str) -> str:
    ATTEMPTS["sms"] += 1
    print(f"  SMS attempt {ATTEMPTS['sms']}", flush=True)
    if ATTEMPTS["sms"] <= int(os.environ.get("SMS_FAILS", "0")):
        raise SmsTimeout("the SMS gateway did not answer in 10 seconds")
    return _record(f"{job}: SMS sent to the citizen")
