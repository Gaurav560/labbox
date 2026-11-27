"""Privacy and prompt injection: keep personal data out of logs, and never let an email give orders.
Run it with: python privacy.py"""
import json
import re

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")
ID12 = re.compile(r"(?<!\d)\d{4} \d{4} \d{4}(?!\d)")  # a 12-digit ID written in groups of four, like an Aadhaar number
PHONE = re.compile(r"$^")  # TODO (task redact_pii): an Indian mobile number (see the lesson)


def redact(text):
    """The text with personal data replaced: 12-digit IDs by [ID], email addresses by [EMAIL], mobile numbers by [PHONE].
    Policy numbers, registrations, dates and amounts stay: an adjuster needs them, and they are not about a person."""
    # TODO (task redact_pii): replace ID12 first, then EMAIL, then PHONE (use .sub).
    return text

# Phrases that give orders to a program instead of describing a claim. Lower case; matched ignoring case.
SUSPICIOUS = [
    r"ignore (all |any |your |the )?(previous |prior |above )?instructions",
    r"you are now",
    r"system prompt",
    r"approve (this|the|my) claim",
    r"pay (me|this claim) (now|immediately)",
]


def instruction_flags(text):
    """The SUSPICIOUS phrases found in the text, as they were written there, in the order of SUSPICIOUS."""
    # TODO (task instruction_guard): for each pattern, re.search(pattern, text, re.IGNORECASE); keep match.group(0).
    return []


def guard_draft(draft, text):
    """The draft, made "refer" with one more reason when the email contains instructions. Returns a new dict."""
    # TODO (task instruction_guard): no flags -> the draft unchanged. Otherwise {"draft": "refer", "reasons": the old
    # reasons + ["the email contains instructions to Claimdesk"], "flags": the flags}.
    return draft


def log_record(email_id, text, fields, problem):
    """What Claimdesk writes to its log for one email: enough to debug, nothing personal."""
    return {
        "email_id": email_id,
        "chars": len(text),
        "excerpt": redact(text[:160]),
        "fields_read": sorted(k for k, v in (fields or {}).items() if v is not None),
        "problem": problem,
        "flags": instruction_flags(text),
    }


if __name__ == "__main__":
    with open("data/inbox.json", encoding="utf-8") as f:
        inbox = json.load(f)
    for email in inbox:
        print(f"--- {email['email_id']}, as the log would keep it:")
        print(redact(email["text"]))
    e30 = inbox[-1]["text"]
    print("--- E-30")
    print("flags:", instruction_flags(e30))
    draft = {"draft": "pay", "reasons": []}  # what chapter 13's /triage drafted for E-30 from the real model's fields
    print("chapter 13 drafted:", draft)
    print("with the guard:   ", guard_draft(draft, e30))
    print("log record:", json.dumps(log_record("E-30", e30, {"policy_no": "DS-POL-41073", "amount_rs": 15750,
                                                            "incident_date": "2026-10-30"}, None)))
