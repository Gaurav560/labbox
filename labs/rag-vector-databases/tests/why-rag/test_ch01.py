import r


def reference(question, sections, k):
    import fieldbook as fb
    asked = fb.words(question)
    scored = [(len(asked & fb.words(s["title"] + " " + s["text"])), n, s) for n, s in enumerate(sections)]
    scored = sorted((x for x in scored if x[0] > 0), key=lambda x: (-x[0], x[1]))
    return [s["id"] for _, _, s in scored[:k]]


def test_keyword_search():
    def check():
        import fieldbook as fb
        sections = fb.load_sections()
        got = fb.keyword_search("How often do we change the camera trap batteries?", sections)
        if not isinstance(got, list) or (got and not isinstance(got[0], dict)):
            return r.failed("keyword_search", "Return a list of the section dicts themselves (with id, title and text), not "
                            "their ids or scores.", "[{'id': 'FM-3.2', ...}, ...]", repr(got)[:80])
        ids = [s["id"] for s in got]
        want = reference("How often do we change the camera trap batteries?", sections, 3)
        if ids != want:
            if sorted(ids) == sorted(want):
                return r.failed("keyword_search", "The right sections, in the wrong order. Best (most shared words) first; "
                                "equal scores keep the manual's order.", want, ids)
            if len(ids) > 3:
                return r.failed("keyword_search", "Return at most k sections (k is 3 unless the caller says otherwise).", want, ids)
            return r.failed("keyword_search", "Score each section by how many of the question's words (words(question)) "
                            "also appear in words(title + ' ' + text).", want, ids)
        if fb.keyword_search("big cat", sections) != []:
            return r.failed("keyword_search", "Sections that share no word with the question must be left out: \"big cat\" "
                            "appears nowhere in the manual, so the answer is [].", [],
                            [s["id"] for s in fb.keyword_search("big cat", sections)])
        for q, k in [("tiger leopard gaur bear snake elephant", 5), ("drone permit form", 2), ("fire season towers", 4)]:
            if [s["id"] for s in fb.keyword_search(q, sections, k=k)] != reference(q, sections, k):
                return r.failed("keyword_search", f"Different sections for {q!r} with k={k}. Ties keep the manual's order.",
                                reference(q, sections, k), [s["id"] for s in fb.keyword_search(q, sections, k=k)])
        r.passed("keyword_search", "Your first retriever: the sections that share the most words with the question. Fast, "
                 "simple, and blind to meaning, as \"big cat\" shows.")
    r.task("keyword_search", check)


def test_context_prompt():
    def check():
        import fieldbook as fb
        sections = fb.load_sections()[9:11]
        q = "What do I do if I meet a tiger?"
        got = fb.build_prompt(q, sections)
        if not isinstance(got, list) or len(got) != 2:
            return r.failed("context_prompt", "Return a list of two messages: the system message and one user message.", 2,
                            len(got) if isinstance(got, list) else type(got).__name__)
        if got[0] != {"role": "system", "content": fb.SYSTEM}:
            return r.failed("context_prompt", "The first message is {\"role\": \"system\", \"content\": SYSTEM}.",
                            {"role": "system", "content": fb.SYSTEM[:40] + "..."}, repr(got[0])[:80])
        user = got[1]
        if user.get("role") != "user":
            return r.failed("context_prompt", "The second message has the role \"user\".", "user", user.get("role"))
        text = user.get("content", "")
        if not text.startswith("Manual sections:"):
            return r.failed("context_prompt", "Start the user message with \"Manual sections:\".", "Manual sections:", text[:30])
        for s in sections:
            if f"[{s['id']}] {s['title']}\n{s['text']}" not in text:
                return r.failed("context_prompt", "Write each section as \"[FM-4.2] Meeting a tiger\" on one line and its text "
                                "on the next, so the model can name the section it used.",
                                f"[{s['id']}] {s['title']}\\n{s['text'][:30]}...", text[:120])
        if not text.rstrip().endswith(f"Question: {q}"):
            return r.failed("context_prompt", "End the user message with \"Question: \" and the question.", f"Question: {q}", text[-60:])
        r.passed("context_prompt", "Retrieval plus generation: the model now reads the manual's sections before it answers. "
                 "That is RAG, in two functions.")
    r.task("context_prompt", check)
