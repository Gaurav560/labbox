import r

TEXT = "The tap water tastes of rust since the storm."


def test_find_checkpoint():
    def check():
        from ticket import build_graph, snapshot_before
        app = build_graph()
        app.invoke({"text": TEXT}, {"configurable": {"thread_id": "C-1"}})
        snap = snapshot_before(app, "C-1", "route")
        if snap is None or snap.next != ("route",) or snap.values.get("kind") != "other":
            return r.failed("find_checkpoint", "Return the snapshot from app.get_state_history(...) whose .next == (node,).",
                            "the checkpoint after triage (kind other, next route)", None if snap is None else snap.next)
        if snapshot_before(app, "C-1", "nowhere") is not None:
            return r.failed("find_checkpoint", "Return None when no checkpoint was about to run that node.")
        r.passed("find_checkpoint", "You found the exact moment between triage and route.")
    r.task("find_checkpoint", check)


def test_correct_and_rerun():
    def check():
        from ticket import build_graph, correct
        app = build_graph()
        config = {"configurable": {"thread_id": "C-2"}}
        app.invoke({"text": TEXT}, config)
        state = correct(app, "C-2", {"kind": "dirty_water", "severity": "urgent"}) or {}
        want = "Your complaint is with the health team. We will respond within 4 hours."
        if state.get("reply") != want:
            return r.failed("correct_and_rerun", "update_state(snapshot.config, fields, as_node=\"triage\"), then invoke(None, "
                            "<the config it returns>) (finish find_checkpoint first).", want, state.get("reply"))
        sources = [s.metadata["source"] for s in app.get_state_history(config)]
        if "update" not in sources:
            return r.failed("correct_and_rerun", "Change the old checkpoint with app.update_state, not with a new invoke.")
        r.passed("correct_and_rerun", "A new branch from the corrected step: health team, 4 hours. The old run is still in the history.")
    r.task("correct_and_rerun", check)
