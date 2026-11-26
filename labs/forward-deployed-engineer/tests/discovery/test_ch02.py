import r


def email(subject, body=""):
    return {"subject": subject, "body": body, "minutes": "5"}


def test_classify_email():
    def check():
        from discovery import classify
        cases = [
            (email("Photos for claim DS-26-10014", "attached"), "photos"),
            (email("Re: PHOTO needed"), "photos"),
            (email("Where is my claim?"), "status"),
            (email("Any update?", "status please"), "status"),
            (email("New claim - scooter theft", "FIR attached"), "new_claim"),
            (email("Invoice from garage"), "documents"),
            (email("Escalation", "pending for a month"), "complaint"),
            (email("Hello", "Thank you for the help."), "other"),
        ]
        for e, want in cases:
            got = classify(e)
            if got != want:
                hint = ""
                if want == "photos" and got == "documents":
                    hint = " Check \"photo\" first: a photo email often says \"attached\" too, and it belongs with photos."
                if want == "new_claim" and got == "documents":
                    hint = " Check \"new claim\" before the document words: a new claim often has an attachment."
                return r.failed("classify_email", f"For the subject {e['subject']!r} the kind should be {want!r}. Look in the subject and the "
                                f"body together, lower-cased, and test the kinds in the order of the TODO.{hint}", want, got)
        r.passed("classify_email", "Simple rules, in a careful order, sorted 40 real emails. Discovery starts with counting, not with a model.")
    r.task("classify_email", check)


def test_costliest_kind():
    def check():
        from discovery import costliest, load_inbox
        got = costliest(load_inbox())
        if got != ("photos", 44.6):
            if isinstance(got, tuple) and got and got[0] == "photos":
                return r.failed("costliest_kind", "Photos is right. Its share is 207 of 464 minutes: 207 / 464 * 100, rounded to 1 decimal.",
                                ("photos", 44.6), got)
            return r.failed("costliest_kind", "Add up the minutes per kind (minutes_by_kind does that), take the kind with the most minutes, "
                            "not the most emails, and its share of all minutes.", ("photos", 44.6), got)
        small = [{"subject": "status?", "body": "", "minutes": "2"}, {"subject": "status", "body": "", "minutes": "2"},
                 {"subject": "photo", "body": "", "minutes": "10"}]
        if costliest(small) != ("photos", 71.4):
            return r.failed("costliest_kind", "Two quick status emails (4 minutes) cost less than one photo email (10 minutes): rank by "
                            "minutes, not by count.", ("photos", 71.4), costliest(small))
        r.passed("costliest_kind", "Status emails are many but quick; photo emails cost 44.6% of the time. That is the problem to solve first.")
    r.task("costliest_kind", check)
