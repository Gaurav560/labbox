"""The day-five demo: Claimdesk as a small web service. POST a claim email to /triage and get a draft for the adjuster.
Run it with: uvicorn app:app --port 8000   then: curl -s localhost:8000/triage -H 'content-type: application/json' -d @data/sample.json"""
import sqlite3

from fastapi import FastAPI
from pydantic import BaseModel, Field

from extract import safe_extract

app = FastAPI(title="Claimdesk")
PILOT_LIMIT_RS = 50000


def get_policy(policy_no, path="data/claimdesk.db"):
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    row = con.execute("SELECT * FROM policies WHERE policy_no = ?", (policy_no,)).fetchone()
    con.close()
    return dict(row) if row else None


@app.get("/health")
def health():
    return {"ok": True}


class TriageIn(BaseModel):
    email: str = Field(min_length=20, max_length=8000)


@app.post("/triage")
def triage(body: TriageIn):
    """Reads the email, looks up the policy, and drafts "pay" or "refer to adjuster" with the reasons."""
    fields, problem = safe_extract(body.email)
    if problem is not None:
        return {"draft": "refer", "reasons": ["could not read the email: " + problem]}
    reasons = []
    policy = None
    if not fields.policy_no:
        reasons.append("no policy number")
    else:
        policy = get_policy(fields.policy_no)
        if policy is None:
            reasons.append("unknown policy")
    if policy:
        if fields.vehicle_reg and fields.vehicle_reg != policy["vehicle_reg"]:
            reasons.append("registration does not match the policy")
        if fields.incident_date and not (policy["start_date"] <= fields.incident_date <= policy["end_date"]):
            reasons.append("incident outside the policy period")
    if fields.amount_rs is None:
        reasons.append("no amount")
    elif fields.amount_rs > PILOT_LIMIT_RS:
        reasons.append("above the pilot limit")
    return {"draft": "pay" if not reasons else "refer", "reasons": reasons, "fields": fields.model_dump()}
