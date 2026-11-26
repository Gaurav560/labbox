import r

OPEN = {"received_at": "2026-08-03 10:00", "decided_at": ""}
TWO_DAYS = {"received_at": "2026-08-03 10:00", "decided_at": "2026-08-05 10:00"}
HALF = {"received_at": "2026-08-03 10:00", "decided_at": "2026-08-03 22:00"}


def test_baseline_days():
    def check():
        from baseline import baseline_days, days_to_decide, load_claims
        if days_to_decide(OPEN) is not None:
            return r.failed("baseline_days", "A claim with an empty decided_at is still open: days_to_decide should return None for it, "
                            "so it is left out of the average instead of counting as 0 days.", None, days_to_decide(OPEN))
        got = days_to_decide(TWO_DAYS)
        if got is None or abs(got - 2.0) > 1e-9:
            return r.failed("baseline_days", "From 3 August 10:00 to 5 August 10:00 is 2 days. Turn both strings into datetimes with "
                            "datetime.strptime(text, FMT) and divide the difference's total_seconds() by 86400.", 2.0, got)
        if abs((days_to_decide(HALF) or 0) - 0.5) > 1e-9:
            return r.failed("baseline_days", "12 hours should be 0.5 days: use total_seconds() / 86400, not .days (which drops the hours).",
                            0.5, days_to_decide(HALF))
        if baseline_days([TWO_DAYS, HALF, OPEN]) != 1.2:
            return r.failed("baseline_days", "The average of 2 days and 0.5 days, with the open claim left out, is 1.25, rounded to 1.2. "
                            "Skip the None values before dividing, and round to 1 decimal place.", 1.2, baseline_days([TWO_DAYS, HALF, OPEN]))
        got = baseline_days(load_claims())
        if got != 12.5:
            return r.failed("baseline_days", "On Deccan Shield's real export the average should be 12.5 days.", 12.5, got)
        r.passed("baseline_days", "12.5 days is the number every later chapter is measured against. Without it, \"faster\" means nothing.")
    r.task("baseline_days", check)


def test_adjuster_hours():
    def check():
        from baseline import adjuster_hours, load_claims
        claims = load_claims()
        got = adjuster_hours(claims)
        if got != 10.8:
            if got == round(len(claims) * 35 / 60, 1):
                return r.failed("adjuster_hours", "That is the hours for the whole quarter. Divide by the 13 weeks first: claims per week is "
                                "len(claims) / weeks.", 10.8, got)
            return r.failed("adjuster_hours", "240 claims over 13 weeks is 18.5 claims a week; at 35 minutes each that is 10.8 hours.", 10.8, got)
        if adjuster_hours(claims[:26], minutes_per_claim=60, weeks=2) != 13.0:
            return r.failed("adjuster_hours", "Use the minutes_per_claim and weeks arguments, not fixed numbers: 26 claims over 2 weeks at 60 "
                            "minutes is 13.0 hours a week.", 13.0, adjuster_hours(claims[:26], minutes_per_claim=60, weeks=2))
        r.passed("adjuster_hours", "Hours of people's time are what a customer feels, and pays for. You can now say what the problem costs.")
    r.task("adjuster_hours", check)
