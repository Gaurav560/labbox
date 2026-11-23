import r


def test_first_graph():
    def check():
        from graph import build_graph
        g = build_graph()
        if not hasattr(g, "invoke"):
            return r.failed("first_graph", "build_graph() returned an uncompiled StateGraph. Add the nodes and edges, then return graph.compile().")
        final = g.invoke({"text": "Brown water from the tap"})
        if final.get("kind") != "dirty_water" or "4 hours" not in final.get("reply", ""):
            return r.failed("first_graph", "The graph should run classify, then write_reply: START -> classify -> write_reply -> END.",
                            "kind dirty_water and a reply promising 4 hours", final)
        r.passed("first_graph", "Two nodes, three edges, one state: a complaint went in and came out classified with a reply.")
    r.task("first_graph", check)


def test_trace_steps():
    def check():
        from graph import build_graph, steps
        if not hasattr(build_graph(), "invoke"):
            return r.failed("trace_steps", "First build the graph (the task above).")
        got = steps("Pipe burst near the school")
        if got != ["classify", "write_reply"]:
            return r.failed("trace_steps", "Collect the node name of every update from stream(..., stream_mode=\"updates\"), in order.",
                            ["classify", "write_reply"], got)
        r.passed("trace_steps", "A graph is observable: every node reports when it has run, in order.")
    r.task("trace_steps", check)
