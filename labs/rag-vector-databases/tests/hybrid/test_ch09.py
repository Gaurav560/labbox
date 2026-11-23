import math

import r


def reference(query, docs, k1=1.5, b=0.75):
    n = len(docs)
    avg = sum(len(d) for d in docs) / n
    out = [0.0] * n
    for term in set(query):
        df = sum(1 for d in docs if term in d)
        if not df:
            continue
        idf = math.log((n - df + 0.5) / (df + 0.5) + 1)
        for i, d in enumerate(docs):
            tf = d.count(term)
            if tf:
                out[i] += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * len(d) / avg))
    return out


def test_bm25_scores():
    def check():
        import numpy as np
        import fieldbook as fb
        docs = [["camera", "trap", "ct-117", "missing"], ["camera", "trap", "batteries", "camera"], ["tiger", "seen"],
                ["the", "camera", "the", "the", "the", "the", "the", "the"]]
        for query in (["camera"], ["ct-117"], ["camera", "batteries", "camera"], ["elephant"], ["the", "camera"]):
            got = fb.bm25_scores(query, docs)
            want = reference(query, docs)
            if not isinstance(got, np.ndarray) or len(got) != len(docs):
                return r.failed("bm25_scores", "Return a NumPy array with one score per document.", len(docs), len(got) if hasattr(got, "__len__") else got)
            if not np.allclose(got, want, atol=1e-6):
                tip = {"elephant": "A term no document contains adds nothing (df is 0: skip it).",
                       }.get(query[0], "Check the formula: idf = log((n - df + 0.5) / (df + 0.5) + 1), and each document gains "
                                       "idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * len(doc) / average_length)).")
                if len(query) != len(set(query)):
                    tip = "Count each distinct query term once: loop over set(query)."
                return r.failed("bm25_scores", f"{tip} Query {query}:", [round(x, 3) for x in want], [round(float(x), 3) for x in got])
        corpus = fb.load_corpus()
        toks = [fb.tokens(fb.chunk_text(c)) for c in corpus]
        best = corpus[int(np.argmax(fb.bm25_scores(fb.tokens("CT-112"), toks)))]["id"]
        if best != "R-0301":
            return r.failed("bm25_scores", "On the real chunks, CT-112 should find report R-0301 first.", "R-0301", best)
        r.passed("bm25_scores", "BM25, the ranking formula behind Elasticsearch, Lucene and most search boxes since the 1990s: exact words, rare ones counted most.")
    r.task("bm25_scores", check)


def test_rrf_fuse():
    def check():
        import fieldbook as fb
        cases = [(([["a", "b"], ["b", "c"]], 60), ["b", "a", "c"]), (([["x", "y", "z"]], 60), ["x", "y", "z"]),
                 (([["a", "b", "c"], ["c", "b", "a"], ["c"]], 60), ["c", "a", "b"]), (([["a", "b"], ["b", "a"], ["a"]], 1), ["a", "b"])]
        for (rankings, k), want in cases:
            got = fb.rrf(rankings, k=k)
            if list(got) != want:
                if list(got) == want[::-1]:
                    return r.failed("rrf_fuse", "Highest total first: sort by the fused score in descending order.", want, list(got))
                return r.failed("rrf_fuse", f"rrf({rankings}, k={k}): each ranking gives 1 / (k + rank), rank starting at 1.", want, list(got))
        r.passed("rrf_fuse", "Reciprocal rank fusion: rankings merged by position alone, so scores on different scales never need to be compared.")
    r.task("rrf_fuse", check)
