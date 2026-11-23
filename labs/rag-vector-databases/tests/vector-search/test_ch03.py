import r


def test_normalize():
    def check():
        import numpy as np
        import fieldbook as fb
        one = fb.normalize([3, 4])
        if not np.allclose(one, [0.6, 0.8]):
            return r.failed("normalize", "A single vector [3, 4] has length 5, so it becomes [0.6, 0.8].", [0.6, 0.8], np.round(one, 3).tolist())
        m = np.array([[3, 4], [1, 0], [0, 2]], dtype=np.float32)
        got = fb.normalize(m)
        if np.allclose(got, m / np.linalg.norm(m)):
            return r.failed("normalize", "Every row needs its own length: pass axis=-1 and keepdims=True to np.linalg.norm, "
                            "or the whole matrix is divided by one number.", [[0.6, 0.8], [1, 0], [0, 1]], np.round(got, 3).tolist())
        if not np.allclose(got, [[0.6, 0.8], [1, 0], [0, 1]], atol=1e-5):
            return r.failed("normalize", "Each row divided by its own length.", [[0.6, 0.8], [1, 0], [0, 1]], np.round(got, 3).tolist())
        if got.dtype != np.float32:
            return r.failed("normalize", "Return float32.", "float32", got.dtype)
        r.passed("normalize", "Length-1 vectors: now a dot product is the cosine, and a whole matrix can be scored in one product.")
    r.task("normalize", check)


def test_top_k():
    def check():
        import numpy as np
        import fieldbook as fb
        rng = np.random.default_rng(3)
        m = rng.standard_normal((2000, 32)).astype(np.float32)
        m /= np.linalg.norm(m, axis=1, keepdims=True)
        q = m[17] * 0.9 + m[400] * 0.1
        q /= np.linalg.norm(q)
        scores = m @ q
        want = [int(i) for i in np.argsort(-scores)[:5]]
        got = fb.top_k(q, m, k=5)
        if not isinstance(got, list) or len(got) != 5:
            return r.failed("top_k", "Return a list of k (row, score) pairs.", 5, len(got) if isinstance(got, list) else type(got).__name__)
        rows = [row for row, _ in got]
        if rows != want:
            if sorted(rows) == sorted(want):
                return r.failed("top_k", "The right rows, not sorted: argpartition finds the best k but leaves them in any "
                                "order. Sort those k by score, best first.", want, rows)
            if rows == [int(i) for i in np.argsort(scores)[:5]]:
                return r.failed("top_k", "Those are the 5 worst rows: partition the negative scores (-scores) so the highest come first.", want, rows)
            return r.failed("top_k", "Score every row with matrix @ query and take the highest.", want, rows)
        if not all(isinstance(row, int) and isinstance(s, float) for row, s in got):
            return r.failed("top_k", "Return plain Python ints and floats (int(i), float(score)), not NumPy numbers.")
        if not r.close(got[0][1], scores[want[0]]):
            return r.failed("top_k", "Each pair is (row, that row's score).", round(float(scores[want[0]]), 4), round(got[0][1], 4))
        if len(fb.top_k(q, m[:3], k=10)) != 3:
            return r.failed("top_k", "When k is larger than the number of rows, return every row (k = min(k, rows)).", 3, len(fb.top_k(q, m[:3], k=10)))
        r.passed("top_k", "Exact nearest neighbours: one matrix product and a partial sort. Every vector database is measured against this answer.")
    r.task("top_k", check)
