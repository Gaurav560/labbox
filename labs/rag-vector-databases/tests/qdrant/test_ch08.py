import r


def corpus():
    import numpy as np
    import fieldbook as fb
    chunks = fb.load_corpus()
    vectors = fb.normalize(np.random.default_rng(0).standard_normal((len(chunks), 16)).astype(np.float32))
    return fb, chunks, vectors


def test_make_store():
    def check():
        from qdrant_client import QdrantClient, models
        fb, chunks, vectors = corpus()
        client = fb.make_store(chunks, vectors)
        if not isinstance(client, QdrantClient):
            return r.failed("make_store", "Return the QdrantClient.", "QdrantClient", type(client).__name__)
        if not client.collection_exists(fb.COLLECTION):
            return r.failed("make_store", f"Create the collection named COLLECTION ({fb.COLLECTION!r}).")
        params = client.get_collection(fb.COLLECTION).config.params.vectors
        if params.size != 16:
            return r.failed("make_store", "The collection's vector size is vectors.shape[1] (here 16), not a fixed 384.", 16, params.size)
        if params.distance != models.Distance.COSINE:
            return r.failed("make_store", "Compare vectors by cosine distance (models.Distance.COSINE).", "Cosine", params.distance)
        count = client.count(fb.COLLECTION).count
        if count != len(chunks):
            return r.failed("make_store", "One point per chunk.", len(chunks), count)
        point = client.retrieve(fb.COLLECTION, ids=[7], with_payload=True, with_vectors=True)
        if not point or point[0].payload != chunks[7]:
            return r.failed("make_store", "Point 7's payload should be chunk 7 itself (id = position in the list).")
        r.passed("make_store", "A collection of points: id, vector and payload, the same three things in every vector database.")
    r.task("make_store", check)


def test_filtered_search():
    def check():
        import numpy as np
        from qdrant_client import QdrantClient, models
        fb, chunks, vectors = corpus()
        client = QdrantClient(":memory:")
        client.create_collection(fb.COLLECTION, vectors_config=models.VectorParams(size=16, distance=models.Distance.COSINE))
        client.upsert(fb.COLLECTION, points=[models.PointStruct(id=i, vector=v.tolist(), payload=c) for i, (c, v) in enumerate(zip(chunks, vectors))])
        q = vectors[3]
        scores = vectors @ q

        def ref(k, kind=None, zone=None):
            ok = [i for i, c in enumerate(chunks) if (kind is None or c["kind"] == kind) and (zone is None or c["zone"] == zone)]
            return [chunks[i]["id"] for i in sorted(ok, key=lambda i: -scores[i])[:k]]

        for options in ({}, {"kind": "report"}, {"zone": "buffer"}, {"kind": "report", "zone": "core"}):
            got = fb.filtered_search(client, q, k=4, **options)
            if not isinstance(got, list) or (got and not isinstance(got[0], dict)):
                return r.failed("filtered_search", "Return a list of dicts: each hit's payload with \"score\" added.")
            if [h.get("id") for h in got] != ref(4, **options):
                return r.failed("filtered_search", f"With {options or 'no filter'}, keep only the chunks whose payload matches "
                                "every given value (conditions under must).", ref(4, **options), [h.get("id") for h in got])
            if got and ("score" not in got[0] or abs(got[0]["score"] - float(scores[[c["id"] for c in chunks].index(got[0]["id"])])) > 1e-3):
                return r.failed("filtered_search", "Add each hit's score to its payload dict under \"score\".")
        r.passed("filtered_search", "Search by meaning, but only among the chunks that match: payload filters are what make a vector database more than a matrix.")
    r.task("filtered_search", check)
