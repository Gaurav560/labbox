"""Way 1: a person writes the rules. Fast and clear, and blind to anything nobody wrote a rule for."""

OFFICE = "The co-op office is open Monday to Saturday, 9:00 to 17:00."
ONION = "Today's onion rate is Rs 1,850 a quintal."
UNKNOWN = "Sorry, I only know the office hours and the onion rate."


def rule_reply(message: str) -> str:
    text = message.lower()
    if "office" in text or "open" in text:
        return OFFICE
    if "price" in text or "rate" in text:
        return ONION
    return UNKNOWN
