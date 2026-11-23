"""The water board's rules for complaints, written as plain Python (no model yet)."""

KINDS = {
    "dirty_water": ["dirty", "smell", "brown", "muddy", "worms"],
    "no_water": ["no water", "dry", "not coming", "no supply"],
    "leak": ["leak", "burst", "pipe broken", "flooding"],
    "billing": ["bill", "charged", "payment", "meter"],
}

SEVERITY = {"dirty_water": "urgent", "no_water": "high", "leak": "high", "billing": "normal", "other": "normal"}
HOURS = {"urgent": 4, "high": 24, "normal": 72}  # promised response time


def kind_of(text: str) -> str:
    """The first kind whose words appear in the complaint, or "other"."""
    lowered = text.lower()
    for kind, words in KINDS.items():
        if any(word in lowered for word in words):
            return kind
    return "other"
