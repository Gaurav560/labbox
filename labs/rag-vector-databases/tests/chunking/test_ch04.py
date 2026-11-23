import r


def test_word_chunks():
    def check():
        import fieldbook as fb
        ten = " ".join(str(i) for i in range(1, 11))
        cases = [(("a b c d e f g", 3, 1), ["a b c", "c d e", "e f g"]),
                 ((ten, 4, 0), ["1 2 3 4", "5 6 7 8", "9 10"]),
                 ((ten, 4, 2), ["1 2 3 4", "3 4 5 6", "5 6 7 8", "7 8 9 10"]),
                 (("a b c d", 10, 2), ["a b c d"])]
        for (text, size, overlap), want in cases:
            got = fb.word_chunks(text, size, overlap)
            if got != want:
                if got[:len(want)] == want:
                    return r.failed("word_chunks", f"One window too many for size={size}, overlap={overlap}: stop after the window "
                                    "that reaches the last word, or the end is repeated in a short extra chunk.", want, got)
                return r.failed("word_chunks", f"Windows of size={size} words starting every size - overlap = {size - overlap} words.", want, got)
        r.passed("word_chunks", "Fixed windows with overlap: the simplest chunker, and the default in most libraries.")
    r.task("word_chunks", check)


def test_section_chunks():
    def check():
        from pathlib import Path
        import fieldbook as fb
        small = "# A title\n\nIntro text.\n\n## X-1 First one\nSome   text\nover two lines.\n\n## X-2 Second\nMore."
        got = fb.section_chunks(small)
        want = [{"id": "X-1", "title": "First one", "text": "Some text over two lines."}, {"id": "X-2", "title": "Second", "text": "More."}]
        if got != want:
            if got and got[0].get("title") == "A title":
                return r.failed("section_chunks", "Skip the piece before the first \"## \" section: it is the document's title, not a section.", want, got)
            if got and got[0].get("text") != want[0]["text"]:
                return r.failed("section_chunks", "Squeeze the text: \" \".join(body.split()) turns line breaks and runs of spaces into single spaces.",
                                want[0]["text"], got[0].get("text"))
            return r.failed("section_chunks", "One dict per section: the heading's first word is the id, the rest the title.", want, got)
        manual = fb.section_chunks(Path("data/manual.md").read_text())
        if len(manual) != 31 or manual[10]["id"] != "FM-4.2" or manual[10]["title"] != "Meeting a tiger":
            return r.failed("section_chunks", "The manual has 31 sections, the eleventh FM-4.2 Meeting a tiger.", 31, len(manual))
        r.passed("section_chunks", "Chunks that follow the document's own structure, each with an id and a title: the best "
                 "of the six ways measured in this chapter.")
    r.task("section_chunks", check)
