import r

HITS = [{"id": "R-0410", "title": "Patrol report R-0410", "text": "...", "kind": "report", "zone": "buffer", "rerank": 5.4321},
        {"id": "FM-4.3", "title": "Leopards near villages", "text": "...", "kind": "manual", "zone": "all", "rerank": -1.236}]


def test_search_endpoint():
    def check():
        from fastapi.testclient import TestClient
        import app
        calls = []
        app.find = lambda q, kind=None, zone=None, k=5: calls.append((q, kind, zone, k)) or [dict(h) for h in HITS]
        res = TestClient(app.app).get("/search", params={"q": "leopard in a village", "kind": "report", "zone": "buffer", "k": 2})
        if res.status_code != 200:
            return r.failed("search_endpoint", f"GET /search answered {res.status_code}. Look at the terminal running the check for the error.", 200, res.status_code)
        if calls != [("leopard in a village", "report", "buffer", 2)]:
            return r.failed("search_endpoint", "Pass q, kind, zone and k on to find().", [("leopard in a village", "report", "buffer", 2)], calls)
        want = {"query": "leopard in a village", "results": [{"id": "R-0410", "title": "Patrol report R-0410", "score": 5.43},
                                                             {"id": "FM-4.3", "title": "Leopards near villages", "score": -1.24}]}
        if res.json() != want:
            return r.failed("search_endpoint", "Answer {\"query\": q, \"results\": [{\"id\", \"title\", \"score\"}, ...]}, with the rerank score rounded to 2 places.", want, res.json())
        r.passed("search_endpoint", "GET /search: filters, two-stage retrieval and scores, as JSON any client can use.")
    r.task("search_endpoint", check)


def test_ask_endpoint(fake):
    def check():
        from fastapi.testclient import TestClient
        import app
        app.client.cache_clear()
        calls = []
        app.find = lambda q, kind=None, zone=None, k=5: calls.append((q, kind, zone)) or [dict(h) for h in HITS]
        fake.script = lambda body: "Keep people back and call Vanrai Base [1]."
        res = TestClient(app.app).post("/ask", json={"question": "A leopard is in the village. What do we do?"})
        if res.status_code != 200:
            return r.failed("ask_endpoint", f"POST /ask answered {res.status_code}.", 200, res.status_code)
        if not calls or calls[0][1:] != (None, None):
            return r.failed("ask_endpoint", "Find the chunks for body.question with no filters.", "find(question)", calls)
        want = {"answer": "Keep people back and call Vanrai Base [1].", "sources": ["R-0410", "FM-4.3"]}
        if res.json() != want:
            return r.failed("ask_endpoint", "Return what answer(question, chunks, client()) gives.", want, res.json())
        if len(fake.chat_requests) != 1 or "[1] R-0410" not in fake.chat_requests[0]["messages"][1]["content"]:
            return r.failed("ask_endpoint", "The model should receive the grounded messages for the found chunks.")
        r.passed("ask_endpoint", "Fieldbook is a service: a question in, an answer with its sources out, and an honest \"not found\" when the manual is silent.")
    r.task("ask_endpoint", check)
