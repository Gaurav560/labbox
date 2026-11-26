"""A read-only copy of Deccan Shield's policy database (SQLite): a policies table and a claims table.
Run it with: python db.py"""
import sqlite3


def connect(path="data/policies.db"):
    """Opens the database read-only: Claimdesk reads the customer's data, it never changes it."""
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def policy_for_claim(con, claim_id):
    """The policy behind a claim as a dict (policy_no, holder, vehicle_reg, vehicle, start_date, end_date, sum_insured,
    deductible), or None for an unknown claim."""
    # TODO (task policy_for_claim): one SELECT p.* FROM claims c JOIN policies p ON p.policy_no = c.policy_no
    # WHERE c.claim_id = ?, with claim_id passed as a parameter, never pasted into the SQL text. dict(row), or None.
    return None


def lapsed_claims(con):
    """Claims received after their policy had ended: (claim_id, end_date, received_day) tuples, ordered by claim_id."""
    # TODO (task lapsed_claims): JOIN the same way. received_day is substr(c.received_at, 1, 10) (the date part); keep
    # the rows where it is later than p.end_date, ORDER BY c.claim_id, and return each row as a tuple.
    return []


if __name__ == "__main__":
    con = connect()
    print(policy_for_claim(con, "DS-26-10038"))
    print(policy_for_claim(con, "DS-26-99999"))
    lapsed = lapsed_claims(con)
    print(f"claims on a lapsed policy: {len(lapsed)}")
    for row in lapsed:
        print("  ", row)
