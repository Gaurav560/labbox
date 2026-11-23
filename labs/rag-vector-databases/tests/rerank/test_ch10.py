import r

CHUNKS = [
    {"id": "A", "title": "Bus timetable", "text": "The bus to Pune leaves at 7 in the morning."},
    {"id": "B", "title": "Meeting a tiger", "text": "If you meet a tiger, stand still and do not run. Back away slowly."},
    {"id": "C", "title": "Tiger census", "text": "The tiger census counts pugmarks every four years."},
    {"id": "D", "title": "Snakebite", "text": "Keep the person still and carry them to the health centre."},
]


def test_rerank():
    def check():
        import numpy as np
        import fieldbook as fb
        q = "What should I do if I meet a tiger on the path?"
        scores = list(fb.reranker().rerank(q, [fb.chunk_text(c) for c in CHUNKS]))
        order = [CHUNKS[i]["id"] for i in np.argsort(scores)[::-1]]
        original = [dict(c) for c in CHUNKS]
        got = fb.rerank(q, CHUNKS, top_n=3)
        if not isinstance(got, list) or len(got) != 3:
            return r.failed("rerank", "Return at most top_n chunks.", 3, len(got) if isinstance(got, list) else type(got).__name__)
        if [c["id"] for c in got] != order[:3]:
            return r.failed("rerank", "Sort by the cross-encoder's scores, highest first.", order[:3], [c["id"] for c in got])
        if not isinstance(got[0].get("rerank"), float) or abs(got[0]["rerank"] - max(scores)) > 1e-3:
            return r.failed("rerank", "Add each chunk's score under \"rerank\", as a float.", round(max(scores), 2), got[0].get("rerank"))
        if CHUNKS != original:
            return r.failed("rerank", "Return copies (dict(chunk, rerank=...)): the original chunks must stay unchanged, because the index keeps using them.")
        r.passed("rerank", "A cross-encoder reads the question and each chunk together, so it sees what a single vector cannot: which chunk answers.")
    r.task("rerank", check)


def test_two_stage():
    def check():
        import fieldbook as fb

        class Stub:
            def __init__(self):
                self.asked = []

            def hybrid(self, question, k=5):
                self.asked.append(k)
                return [dict(c) for c in CHUNKS][:k]

        fb.rerank("tiger", CHUNKS[:1], top_n=1)   # two_stage uses your rerank
        stub = Stub()
        q = "What should I do if I meet a tiger on the path?"
        got = fb.two_stage(q, stub, first=3, final=2)
        if stub.asked != [3]:
            return r.failed("two_stage", "Call index.hybrid(question, k=first) once for the candidates.", [3], stub.asked)
        want = [c["id"] for c in fb.rerank(q, CHUNKS[:3], top_n=2)]
        if [c["id"] for c in got] != want:
            return r.failed("two_stage", "Rerank the candidates and keep the best `final`.", want, [c["id"] for c in got])
        r.passed("two_stage", "Two stages: a fast search casts a wide net, a slow careful model picks from it. Almost every serious search system works this way.")
    r.task("two_stage", check)
