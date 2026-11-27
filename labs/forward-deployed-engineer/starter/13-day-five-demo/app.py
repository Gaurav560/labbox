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
    # TODO (task input_guard): an empty or one-word email, or a 50-page paste, must never reach the model. Give email
    # limits with Field(...): at least 20 characters, at most 8000. FastAPI then answers 422 by itself.
    email: str


@app.post("/triage")
def triage(body: TriageIn):
    """Reads the email, looks up the policy, and drafts "pay" or "refer to adjuster" with the reasons."""
    # TODO (task triage_endpoint): fields, problem = safe_extract(body.email). Then build the reasons list:
    #   - problem is not None -> ["could not read the email: " + problem] and return {"draft": "refer", "reasons": ...}
    #   - no policy_no in the fields -> "no policy number"; else policy = get_policy(...), None -> "unknown policy"
    #   - a policy whose vehicle_reg differs from the email's -> "registration does not match the policy"
    #   - incident_date (when known) outside start_date..end_date -> "incident outside the policy period"
    #   - amount_rs missing -> "no amount"; above PILOT_LIMIT_RS -> "above the pilot limit"
    # Return {"draft": "pay" if there are no reasons else "refer", "reasons": reasons, "fields": fields.model_dump()}.
    return {"draft": "refer", "reasons": ["not written yet"]}
