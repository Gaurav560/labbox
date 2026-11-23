import r


def test_embed_texts():
    def check():
        import numpy as np
        import fieldbook as fb
        texts = ["A tiger crossed the path.", "Change the camera trap batteries every 21 days."]
        got = fb.embed(texts)
        if not isinstance(got, np.ndarray):
            return r.failed("embed_texts", "Return a NumPy array (np.array(...)), not a list or a generator.", "numpy.ndarray", type(got).__name__)
        if got.shape != (2, 384):
            return r.failed("embed_texts", "One row of 384 numbers per text.", (2, 384), got.shape)
        if got.dtype != np.float32:
            return r.failed("embed_texts", "Use dtype float32: half the memory of float64, and what vector databases store.", "float32", got.dtype)
        direct = np.array(list(fb.model().embed(texts)), dtype=np.float32)
        if not np.allclose(got, direct, atol=1e-4):
            return r.failed("embed_texts", "The rows should be the model's vectors for the texts, in the same order.")
        if fb.embed(["only one"]).shape != (1, 384):
            return r.failed("embed_texts", "A list with one text gives a 1 x 384 matrix.", (1, 384), fb.embed(["only one"]).shape)
        r.passed("embed_texts", "Every text is now 384 numbers, made on your own CPU: no API, no cost, the same numbers every time.")
    r.task("embed_texts", check)


def test_cosine():
    def check():
        import fieldbook as fb
        cases = [(([1, 0], [1, 0]), 1.0), (([1, 0], [0, 1]), 0.0), (([1, 0], [-1, 0]), -1.0), (([1, 1], [2, 2]), 1.0),
                 (([3, 4], [4, 3]), 0.96)]
        for (a, b), want in cases:
            got = fb.cosine(a, b)
            if not isinstance(got, float):
                return r.failed("cosine", "Return a plain Python float (float(...)).", "float", type(got).__name__)
            if not r.close(got, want):
                hint = ("Divide by both lengths: [1, 1] and [2, 2] point the same way, so their cosine is 1.0 whatever their size."
                        if (a, b) == ([1, 1], [2, 2]) else "Dot product divided by the product of the two lengths.")
                return r.failed("cosine", hint + f" cosine({a}, {b})", want, round(got, 4))
        r.passed("cosine", "Cosine similarity: how alike two directions are, whatever the lengths. Every vector search ranks by it, or by something equivalent.")
    r.task("cosine", check)
