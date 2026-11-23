import base64
import json

import r
from fake_openai import Reply

JPEG = b"\xff\xd8\xff\xe0fake-jpeg-bytes"


def test_image_message():
    def check():
        from leaf import image_message
        m = image_message("What is this?", JPEG)
        blocks = m.content if isinstance(m.content, list) else []
        if len(blocks) != 2:
            return r.failed("image_message", "Make the content a list of two blocks: a text block and an image block.", 2, len(blocks))
        text, image = blocks
        if text != {"type": "text", "text": "What is this?"}:
            return r.failed("image_message", "The first block is {\"type\": \"text\", \"text\": question}.", {"type": "text", "text": "What is this?"}, text)
        if image.get("type") != "image" or image.get("mime_type") != "image/jpeg":
            return r.failed("image_message", "The second block has \"type\": \"image\" and \"mime_type\": mime_type.")
        if image.get("base64") != base64.b64encode(JPEG).decode():
            return r.failed("image_message", "Put the bytes in as base64 text: base64.b64encode(image).decode().")
        r.passed("image_message", "Text and a picture in one message: LangChain's standard content blocks, the same for every provider.")
    r.task("image_message", check)


def test_leaf_report(fake):
    def check():
        from leaf import LeafReport, leaf_report
        fake.script = lambda b: Reply(json.dumps({"crop": "grapes", "problem": "downy mildew", "confidence": "medium", "next_step": "show the co-op agronomist"}))
        got = leaf_report("What is this?", JPEG)
        if not fake.chat_requests:
            return r.failed("leaf_report", "leaf_report never called the model.")
        user = [m for m in fake.chat_requests[-1]["messages"] if m["role"] == "user"][0]
        parts = user["content"] if isinstance(user["content"], list) else []
        if not any(p.get("type") == "image_url" and p["image_url"]["url"].startswith("data:image/jpeg;base64,") for p in parts):
            return r.failed("leaf_report", "Send your image_message(question, image): the request should carry the photo.")
        from leaf import RULES
        if fake.texts(fake.chat_requests[-1], "system") != [RULES]:
            return r.failed("leaf_report", "Send SystemMessage(RULES) first: Navin must never recommend a chemical.")
        if not isinstance(got, LeafReport) or got.problem != "downy mildew":
            return r.failed("leaf_report", "Return model.with_structured_output(LeafReport).invoke([...]).", "LeafReport", got)
        r.passed("leaf_report", "A photo in, a checked report out: LangChain turned your image block into OpenAI's image_url format.")
    r.task("leaf_report", check)
