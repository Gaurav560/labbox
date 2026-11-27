import r

KEY = "sk-lab-very-secret-123"


def test_settings_from_env():
    def check():
        from settings import ConfigError, settings_from_env
        s = settings_from_env({"OPENAI_BASE_URL": "http://gw/v1", "OPENAI_API_KEY": KEY})
        if (s.base_url, s.api_key, s.pilot_limit_rs, s.prompt_version, s.db_path) != ("http://gw/v1", KEY, 50000, "v1", "data/claimdesk.db"):
            return r.failed("settings_from_env", "With only the two required variables, use the defaults: 50000, \"v1\", \"data/claimdesk.db\".")
        if KEY in repr(s):
            return r.failed("settings_from_env", "The key must never appear when settings are printed (Settings already hides it: build a Settings).")
        s = settings_from_env({"OPENAI_BASE_URL": "u", "OPENAI_API_KEY": KEY, "PILOT_LIMIT_RS": "30000", "PROMPT_VERSION": "v2", "CLAIMDESK_DB": "x.db"})
        if (s.pilot_limit_rs, s.prompt_version, s.db_path) != (30000, "v2", "x.db"):
            return r.failed("settings_from_env", "Read PILOT_LIMIT_RS (as an int), PROMPT_VERSION and CLAIMDESK_DB when they are given.",
                            (30000, "v2", "x.db"), (s.pilot_limit_rs, s.prompt_version, s.db_path))
        cases = [({}, "OPENAI_BASE_URL is not set; OPENAI_API_KEY is not set"),
                 ({"OPENAI_BASE_URL": "u", "OPENAI_API_KEY": ""}, "OPENAI_API_KEY is not set"),
                 ({"OPENAI_API_KEY": KEY, "PILOT_LIMIT_RS": "50k"}, "OPENAI_BASE_URL is not set; PILOT_LIMIT_RS must be a positive whole number of rupees"),
                 ({"OPENAI_BASE_URL": "u", "OPENAI_API_KEY": KEY, "PILOT_LIMIT_RS": "0"}, "PILOT_LIMIT_RS must be a positive whole number of rupees"),
                 ({"OPENAI_BASE_URL": "u", "OPENAI_API_KEY": KEY, "PILOT_LIMIT_RS": "-5"}, "PILOT_LIMIT_RS must be a positive whole number of rupees")]
        for env, want in cases:
            try:
                settings_from_env(env)
            except ConfigError as e:
                if str(e) != want:
                    return r.failed("settings_from_env", f"For {sorted(env)} the message should list every problem, joined by '; '.", want, str(e))
                if KEY in str(e):
                    return r.failed("settings_from_env", "Never put a value in a message, least of all the key.")
                continue
            return r.failed("settings_from_env", f"{env if KEY not in str(env) else sorted(env)} should raise ConfigError: {want}")
        r.passed("settings_from_env", "One message with every problem, no secrets in it, and the same code on a laptop, in CI and in production.")
    r.task("settings_from_env", check)


def test_smoke_test():
    def check():
        from smoke import SMOKE, smoke_test
        seen = []

        def good(email, received_on):
            seen.append(received_on)
            want = {c[1]: c[3] for c in SMOKE}[email]
            return {"draft": want, "reasons": [] if want == "pay" else ["x"]}

        if smoke_test(good) != [] or seen != [c[2] for c in SMOKE]:
            return r.failed("smoke_test", "Call run(email, received_on) for every case; when every draft is right, return [].", [], smoke_test(good))

        def wrong(email, received_on):
            return {"draft": "refer", "reasons": ["above the pilot limit"]}

        if smoke_test(wrong) != ["E-01: expected pay, got refer"]:
            return r.failed("smoke_test", "A wrong draft is reported as '<id>: expected <want>, got <draft>'.", ["E-01: expected pay, got refer"], smoke_test(wrong))

        def broken(email, received_on):
            if "DS-POL-40370" in email:
                raise TimeoutError("slow")
            return {"draft": "pay"}

        got = smoke_test(broken)
        want = ["E-01: no reasons list", "E-24: crashed (TimeoutError)", "E-30: no reasons list"]
        if got != want:
            return r.failed("smoke_test", "Catch exceptions per case (and carry on), and check the reasons list before the draft.", want, got)
        r.passed("smoke_test", "Anyone at Deccan Shield can now ask \"is it working?\" and get a yes or no in ten seconds.")
    r.task("smoke_test", check)
