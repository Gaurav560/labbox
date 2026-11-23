import r


def test_recall_at_k():
    def check():
        import numpy as np
        import fieldbook as fb
        cases = [(([[1, 2, 3]], [[1, 2, 4]]), 2 / 3), (([[1, 2, 3], [7, 8, 9]], [[1, 2, 3], [0, 0, 9]]), (1 + 1 / 3) / 2),
                 ((np.array([[5, 6, 1, 2]]), np.array([[1, 2]])), 0.0), ((np.array([[3, 2, 1]]), np.array([[1, 2, 3]])), 1.0)]
        for (found, truth), want in cases:
            got = fb.recall_at_k(found, truth)
            if not isinstance(got, float):
                return r.failed("recall_at_k", "Return a plain float.", "float", type(got).__name__)
            if not r.close(got, want):
                if r.close(want, 0.0):
                    return r.failed("recall_at_k", "Only the first k found ids count (k is the length of a truth row): [5, 6, 1, 2] "
                                    "against the truth [1, 2] has recall 0, because 1 and 2 came too late.", want, round(got, 3))
                return r.failed("recall_at_k", f"recall_at_k({found if isinstance(found, list) else found.tolist()}, "
                                f"{truth if isinstance(truth, list) else truth.tolist()})", round(want, 3), round(got, 3))
        r.passed("recall_at_k", "Recall: the share of the true neighbours an index found. The number every ANN index trades for speed.")
    r.task("recall_at_k", check)


def test_tune_ef():
    def check():
        import fieldbook as fb
        fb.recall_at_k([[1]], [[1]])          # smallest_ef measures with your recall_at_k
        vectors = fb.fake_embeddings(8000, seed=4)
        queries = fb.fake_embeddings(60, seed=8)
        truth = fb.exact_neighbours(vectors, queries, 10)
        index = fb.hnsw_index(vectors, m=8, ef_construction=40)

        def recall_with(ef):
            index.hnsw.efSearch = ef
            _, found = index.search(queries, 10)
            return sum(len(set(f) & set(t)) / 10 for f, t in zip(found, truth)) / len(truth)

        choices = (16, 32, 64, 128, 256)
        targets = [0.9, 0.97, 0.99]
        for target in targets:
            want = next((ef for ef in choices if recall_with(ef) >= target), None)
            got = fb.smallest_ef(index, queries, truth, k=10, target=target, choices=choices)
            if got != want:
                return r.failed("tune_ef", f"For a target recall of {target}, try the choices smallest first and return the first "
                                "that reaches it (set index.hnsw.efSearch, search, measure).", want, got)
        if fb.smallest_ef(index, queries, truth, k=10, target=1.01, choices=choices) is not None:
            return r.failed("tune_ef", "When no choice reaches the target, return None.")
        r.passed("tune_ef", "Tuning by measurement: the smallest efSearch that meets your recall target is the fastest good-enough search.")
    r.task("tune_ef", check)
