"""The data contract: what a claim must look like before Claimdesk accepts it. Agreed with Deccan Shield's IT team, and
checked in code, so bad rows are rejected with a reason instead of reaching a model. Run it with: python contract.py"""
import csv
import re
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, ValidationError, field_validator

REG = re.compile(r"^[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}$")  # MH12AB1234: state, district, series, number


def load_incoming(path="data/incoming_claims.csv"):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


class Claim(BaseModel):
    """One claim as Claimdesk accepts it."""
    # TODO (task claim_model): the fields and their rules:
    #   claim_id: str, pattern ^DS-26-\d{5}$        policy_no: str, pattern ^DS-POL-\d{5}$
    #   vehicle: Literal["two-wheeler", "car", "commercial"]
    #   amount_rs: int, greater than 0 (Field(gt=0))  received: date
    #   vehicle_reg: str, normalised by a field_validator: upper-case, without spaces or dashes, then it must match REG
    #   (raise ValueError("not a vehicle registration like MH12AB1234") when it does not).
    claim_id: str


def contract_report(rows):
    """(valid, errors): valid is the list of Claim objects; errors a list of (row_no, field, message) for every
    problem in every rejected row. Rows are numbered from 1, like a spreadsheet without its header."""
    # TODO (task contract_report): try Claim(**row) for each row. On ValidationError, go through e.errors(): the field
    # is the first part of err["loc"] and the message err["msg"]. Collect the valid ones and the errors.
    return [], []


if __name__ == "__main__":
    valid, errors = contract_report(load_incoming())
    print(f"accepted: {len(valid)}")
    for c in valid:
        print("  ", c.claim_id, c.vehicle_reg, c.amount_rs)
    print(f"rejected rows: {len(errors)}")
    for row_no, field, message in errors:
        print(f"   row {row_no}: {field}: {message}")
