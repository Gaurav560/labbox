import r


def test_hit_rate():
    def check():
        from quality import hit_rate
        golden = [("a", "x.txt"), ("b", "y.txt"), ("c", "z.txt"), ("d", "x.txt")]
        answers = {"a": ["x.txt", "y.txt"], "b": ["x.txt", "y.txt"], "c": ["x.txt", "y.txt"], "d": ["y.txt", "x.txt"]}
        got1, got2 = hit_rate(answers.get, golden, 1), hit_rate(answers.get, golden, 2)
        if (got1, got2) != (0.25, 0.75):
            return r.failed("hit_rate", "A hit is when the expected file is among the first k sources. Count hits, divide by the number of questions.",
                            "k=1: 0.25, k=2: 0.75", f"k=1: {got1}, k=2: {got2}")
        r.passed("hit_rate", "A number for retrieval quality: change the chunking or the model, and see whether it goes up.")
    r.task("hit_rate", check)


def test_titled_chunks():
    def check():
        from langchain_core.documents import Document
        from quality import titled_chunks
        chunks = [Document("Cold storage\n\nThe charge is Rs 2.", metadata={"source": "storage.txt", "start_index": 0}),
                  Document("Bookings of more than 50 crates need approval.", metadata={"source": "storage.txt", "start_index": 240})]
        got = titled_chunks(chunks, {"storage.txt": "Cold storage"})
        texts = [c.page_content for c in got]
        want = ["Cold storage\n\nThe charge is Rs 2.", "Cold storage: Bookings of more than 50 crates need approval."]
        if texts != want:
            return r.failed("titled_chunks", "Put the title and \": \" in front of each chunk, unless the chunk already starts with it.", want, texts)
        if got[1].metadata != {"source": "storage.txt", "start_index": 240}:
            return r.failed("titled_chunks", "Keep each chunk's metadata.")
        if chunks[1].page_content != "Bookings of more than 50 crates need approval.":
            return r.failed("titled_chunks", "Make new Documents; do not change the ones you were given.")
        r.passed("titled_chunks", "A piece cut from the middle of a file now says what it is about, and is found for the right questions.")
    r.task("titled_chunks", check)
