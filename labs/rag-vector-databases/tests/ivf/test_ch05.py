import r


def data():
    import fieldbook as fb
    vectors = fb.fake_embeddings(5000, seed=5)
    centroids = fb.train_centroids(vectors, 50)
    return fb, vectors, centroids


def test_build_lists():
    def check():
        import numpy as np
        fb, vectors, centroids = data()
        got = fb.build_lists(vectors, centroids)
        nearest = np.argmax(vectors @ centroids.T, axis=1)
        if not isinstance(got, list) or len(got) != len(centroids):
            return r.failed("build_lists", "Return a list with one array per centroid, in centroid order.", len(centroids),
                            len(got) if isinstance(got, list) else type(got).__name__)
        sizes = [len(x) for x in got]
        if sum(sizes) != len(vectors):
            return r.failed("build_lists", "Every vector belongs to exactly one list.", len(vectors), sum(sizes))
        for c, rows in enumerate(got):
            if sorted(int(i) for i in rows) != [int(i) for i in np.flatnonzero(nearest == c)]:
                return r.failed("build_lists", f"List {c} should hold the rows whose nearest centroid is {c} (the highest dot product, np.argmax along each row).")
        r.passed("build_lists", "The inverted lists: every vector filed under its nearest centroid, like books under a shelf label.")
    r.task("build_lists", check)


def test_ivf_search():
    def check():
        import numpy as np
        fb, vectors, centroids = data()
        nearest = np.argmax(vectors @ centroids.T, axis=1)
        lists = [np.flatnonzero(nearest == c) for c in range(len(centroids))]
        q = fb.fake_embeddings(1, seed=9)[0]
        # everything probed: must equal brute force
        got = fb.ivf_search(q, vectors, centroids, lists, k=5, nprobe=len(centroids))
        scores = vectors @ q
        want = [int(i) for i in np.argsort(-scores)[:5]]
        if [row for row, _ in got] != want:
            return r.failed("ivf_search", "With every list probed, IVF must give the brute-force answer. Score the candidates "
                            "against the query and keep the k best, best first, as rows of the full matrix (not positions in "
                            "the candidate array).", want, [row for row, _ in got])
        # one list probed: only that list's rows
        best_list = int(np.argmax(centroids @ q))
        got = fb.ivf_search(q, vectors, centroids, lists, k=5, nprobe=1)
        if not set(row for row, _ in got) <= set(int(i) for i in lists[best_list]):
            return r.failed("ivf_search", "With nprobe=1, only the list of the centroid closest to the query is searched.")
        ref = sorted(((float(scores[i]), int(i)) for i in lists[best_list]), reverse=True)[:5]
        if [row for row, _ in got] != [i for _, i in ref]:
            return r.failed("ivf_search", "The best k rows of the probed lists, best first.", [i for _, i in ref], [row for row, _ in got])
        if not all(isinstance(row, int) and isinstance(s, float) for row, s in got):
            return r.failed("ivf_search", "Return plain Python ints and floats.")
        r.passed("ivf_search", "IVF: look only in the nearest lists. nprobe is the dial between speed and recall.")
    r.task("ivf_search", check)
