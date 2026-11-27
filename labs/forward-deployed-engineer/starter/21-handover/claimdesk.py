"""Claimdesk, as handed over: extraction (chapter 9), the code fixes (chapter 16), the rules (chapters 13 and 19)
and the instruction guard (chapter 17), in one place. triage() is what the service calls for each email."""
import re
import sqlite3
from datetime import date

from openai import OpenAI

from extract import safe_extract

SUSPICIOUS = [
    r"ignore (all |any |your |the )?(previous |prior |above )?instructions",
    r"you are now",
    r"system prompt",
    r"approve (this|the|my) claim",
    r"pay (me|this claim) (now|immediately)",
]


def get_policy(policy_no, path):
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    row = con.execute("SELECT * FROM policies WHERE policy_no = ?", (policy_no,)).fetchone()
    con.close()
    return dict(row) if row else None


def fix_fields(fields, received_on):
    """Chapter 16's fixes. The year is corrected against the day the email arrived, not against today."""
    out = dict(fields)
    for key, value in out.items():
        if isinstance(value, str) and value.lower() == "null":
            out[key] = None
    p = out.get("policy_no")
    squashed = re.sub(r"[\s-]", "", str(p)).upper() if p else ""
    if re.fullmatch(r"DSPOL\d{5}", squashed):
        out["policy_no"] = "DS-POL-" + squashed[-5:]
    d = out.get("incident_date")
    if d:
        arrived = date.fromisoformat(received_on)
        when = date.fromisoformat(d)
        if when.year < arrived.year:
            when = when.replace(year=arrived.year)
            if when > arrived:
                when = when.replace(year=arrived.year - 1)
            out["incident_date"] = when.isoformat()
    return out


def triage(email, received_on, settings, openai=None):
    """{"draft": "pay" or "refer", "reasons": [...], "fields": {...}} for one claim email."""
    openai = openai or OpenAI(base_url=settings.base_url, api_key=settings.api_key, timeout=60, max_retries=2)
    read, problem = safe_extract(email, openai)
    if problem is not None:
        return {"draft": "refer", "reasons": ["could not read the email: " + problem], "fields": None}
    f = fix_fields(read.model_dump(), received_on)
    reasons, policy = [], None
    if not f["policy_no"]:
        reasons.append("no policy number")
    else:
        policy = get_policy(f["policy_no"], settings.db_path)
        if policy is None:
            reasons.append("unknown policy")
    if policy:
        if f["vehicle_reg"] and f["vehicle_reg"] != policy["vehicle_reg"]:
            reasons.append("registration does not match the policy")
        if f["incident_date"] and not (policy["start_date"] <= f["incident_date"] <= policy["end_date"]):
            reasons.append("incident outside the policy period")
    if f["amount_rs"] is None:
        reasons.append("no amount")
    elif f["amount_rs"] > settings.pilot_limit_rs:
        reasons.append("above the pilot limit")
    if f["incident_type"] == "theft":
        reasons.append("theft: investigation team")
    if any(re.search(p, email, re.IGNORECASE) for p in SUSPICIOUS):
        reasons.append("the email contains instructions to Claimdesk")
    return {"draft": "pay" if not reasons else "refer", "reasons": reasons, "fields": f}
