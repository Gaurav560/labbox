import r


def test_add_subgraph():
    def check():
        from desk import build_graph
        ticket = {"ticket": "T-1", "phone": "98220", "text": "My bill is Rs 2,400."}
        spaces = {ns[0].split(":")[0] for ns, _ in build_graph().stream(ticket, stream_mode="updates", subgraphs=True) if ns}
        state = build_graph().invoke(ticket)
        if not str(state.get("verdict", "")).startswith("held"):
            return r.failed("add_subgraph", "The billing graph did not run: graph.add_node(\"billing\", build_billing()).",
                            "held: ...", state.get("verdict"))
        if "billing" not in spaces:
            return r.failed("add_subgraph", "Add the compiled billing graph itself as the node, not a function around it.")
        r.passed("add_subgraph", "The billing office's graph runs inside the desk graph, sharing phone and verdict.")
    r.task("add_subgraph", check)


def test_map_state():
    def check():
        from desk import build_graph
        state = build_graph().invoke({"ticket": "T-2", "phone": "70300", "text": "Pipe burst outside the school."})
        if state.get("repair_log") != ["T-2: crew booked", "T-2: parts ordered"]:
            return r.failed("map_state", "Invoke REPAIRS with {\"job\": state[\"ticket\"]} and return {\"repair_log\": result[\"log\"]}.",
                            ["T-2: crew booked", "T-2: parts ordered"], state.get("repair_log"))
        r.passed("map_state", "A ticket went in as a job, and the job's log came back as the ticket's repair_log.")
    r.task("map_state", check)
