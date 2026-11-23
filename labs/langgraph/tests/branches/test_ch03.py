import r


def run(text, street):
    from graph import build_graph
    return build_graph().invoke({"text": text, "street": street})


def test_route_by_kind():
    def check():
        from graph import choose_team
        cases = [("dirty_water", "health_team"), ("billing", "billing_office"), ("leak", "repair_crew"), ("no_water", "repair_crew"), ("other", "repair_crew")]
        for kind, want in cases:
            got = choose_team({"kind": kind})
            if got != want:
                return r.failed("route_by_kind", f"A {kind} complaint should go to {want}.", want, got)
        final = run("Brown water", "Gandhi Chowk")
        if not final.get("team", "").startswith("health team"):
            return r.failed("route_by_kind", "The conditional edge should send dirty water to the health team.", "health team...", final.get("team"))
        r.passed("route_by_kind", "One conditional edge, three possible paths: the state decides which one runs.")
    r.task("route_by_kind", check)


def test_retry_loop():
    def check():
        found_first = run("No water", "Station Road")
        if found_first.get("tries") != 1 or found_first.get("zone") != "South":
            return r.failed("retry_loop", "A street found at once should go straight on to route: return \"route\" when zone is set.",
                            "1 try, South", f"{found_first.get('tries')} tries, {found_first.get('zone')!r}")
        corrected = run("No water", "Gandi Chowk")
        if corrected.get("tries") != 2 or corrected.get("zone") != "North":
            return r.failed("retry_loop", "A misspelt street should loop back to find_zone once, and be found with the corrected spelling.",
                            "2 tries, North", f"{corrected.get('tries')} tries, {corrected.get('zone')!r}")
        unknown = run("Leak", "Shivaji Path")
        if unknown.get("tries") != 2 or "front desk" not in unknown.get("team", ""):
            return r.failed("retry_loop", "An unknown street should stop after MAX_TRIES attempts and go to ask_citizen.",
                            "2 tries, front desk", f"{unknown.get('tries')} tries, {unknown.get('team')!r}")
        r.passed("retry_loop", "A loop with a limit: try again once with the corrected spelling, then ask a person.")
    r.task("retry_loop", check)
