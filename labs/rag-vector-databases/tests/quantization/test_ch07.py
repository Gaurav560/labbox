import r


def test_quantize_int8():
    def check():
        import numpy as np
        import fieldbook as fb
        m = np.array([[0.5, -0.2, 0.0], [-1.0, 0.1, 0.0], [0.25, 0.4, 0.0]], dtype=np.float32)
        got = fb.quantize_int8(m)
        if not isinstance(got, tuple) or len(got) != 2:
            return r.failed("quantize_int8", "Return a pair: (codes, scales).")
        codes, scales = got
        if codes.dtype != np.int8:
            return r.failed("quantize_int8", "Store the codes as np.int8: one byte each instead of four.", "int8", codes.dtype)
        if scales.dtype != np.float32 or scales.shape != (3,):
            return r.failed("quantize_int8", "One float32 scale per column.", "(3,) float32", f"{scales.shape} {scales.dtype}")
        if np.isnan(scales).any() or not np.isfinite(codes.astype(np.float32)).all() or scales[2] == 0:
            return r.failed("quantize_int8", "A column of zeros has a largest value of 0: give it the scale 1, not 0 (dividing by 0 gives NaN).")
        if not np.allclose(scales[:2], [1.0 / 127, 0.4 / 127], atol=1e-6):
            return r.failed("quantize_int8", "A column's scale is its largest absolute value divided by 127.", [round(1 / 127, 5), round(0.4 / 127, 5)],
                            np.round(scales[:2], 5).tolist())
        if codes.tolist() != [[64, -64, 0], [-127, 32, 0], [32, 127, 0]]:
            return r.failed("quantize_int8", "codes = round(m / scales), as int8 (np.round before astype, or 63.5 is cut to 63).",
                            [[64, -64, 0], [-127, 32, 0], [32, 127, 0]], codes.tolist())
        v = fb.fake_embeddings(2000, seed=2)
        c, s = fb.quantize_int8(v)
        err = float(np.abs(fb.dequantize(c, s) - v).max())
        if err > 0.01:
            return r.failed("quantize_int8", "Back from int8, the numbers should be within about 0.003 of the originals.", "< 0.01", round(err, 4))
        r.passed("quantize_int8", "A quarter of the memory, and the neighbours barely move: scalar quantization is the cheapest saving in a vector database.")
    r.task("quantize_int8", check)


def test_binary_rescore():
    def check():
        import numpy as np
        import fieldbook as fb
        vectors = fb.fake_embeddings(6000, seed=3)
        bits = fb.binary_codes(vectors)
        q = fb.fake_embeddings(1, seed=11)[0]
        distances = fb.hamming(fb.binary_codes(q)[0], bits)
        for candidates in (20, 300):
            shortlist = np.argsort(distances, kind="stable")[:candidates]
            cutoff = distances[shortlist[-1]]
            allowed = set(int(i) for i in np.flatnonzero(distances <= cutoff))
            got = fb.binary_search(q, bits, vectors, k=5, candidates=candidates)
            if not isinstance(got, list) or len(got) != 5:
                return r.failed("binary_rescore", "Return k (row, score) pairs.", 5, len(got) if isinstance(got, list) else type(got).__name__)
            rows = [row for row, _ in got]
            if not set(rows) <= allowed:
                return r.failed("binary_rescore", "Only rows from the shortlist (the smallest Hamming distances) may be returned.")
            scores = [float(vectors[i] @ q) for i in rows]
            if any(abs(a - b) > 1e-4 for a, b in zip(scores, [s for _, s in got])):
                return r.failed("binary_rescore", "Rescore with the full float vectors: each pair's score is vectors[row] @ query.")
            if scores != sorted(scores, reverse=True):
                return r.failed("binary_rescore", "Best first: sort the rescored shortlist by its exact scores.")
        exact = [int(i) for i in np.argsort(-(vectors @ q))[:5]]
        if [row for row, _ in fb.binary_search(q, bits, vectors, k=5, candidates=len(vectors))] != exact:
            return r.failed("binary_rescore", "With every row on the shortlist, rescoring must give the exact answer.", exact,
                            [row for row, _ in fb.binary_search(q, bits, vectors, k=5, candidates=len(vectors))])
        r.passed("binary_rescore", "32 times less memory for the search, and full accuracy back by rescoring a shortlist: the trick behind binary quantization in Qdrant and others.")
    r.task("binary_rescore", check)
