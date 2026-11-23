"""Way 1: a person writes the rules. Fast and clear, and blind to anything nobody wrote a rule for."""

OFFICE = "The co-op office is open Monday to Saturday, 9:00 to 17:00."
ONION = "Today's onion rate is Rs 1,850 a quintal."
UNKNOWN = "Sorry, I only know the office hours and the onion rate."


def rule_reply(message: str) -> str:
    # TODO (task rule_reply): answer with rules on the message, lower-cased:
    #   it mentions "office" or "open" -> OFFICE; it mentions "price" or "rate" -> ONION; anything else -> UNKNOWN.
    return UNKNOWN
