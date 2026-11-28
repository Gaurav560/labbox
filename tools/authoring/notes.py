"""Draw the handwritten-notes page for chapter recaps (an AI image, one per recap).

    cd backend && .venv/bin/python ../tools/authoring/notes.py JOBS.json OUTDIR "a small doodle of ..."

JOBS.json is a list of {name, lines}: name like "springai-07-notes", lines the five or six short lines the
page must say. A job with "sketch" instead of "lines" draws a tall sketchnote page (owner, 25 November: "descriptive,
easy to understand"): {"title", "subtitle", "box", "flow": [4 to 5 short steps], "list_title", "bullets": [3 to 4]},
1024 x 1536. The doodle argument is ignored for sketch pages. A sketch page is a general summary of the whole
chapter, never example data or invented values: COURSE_PRODUCTION.md section 9, "Sketchnote rules" (owner, 28 November). Writes OUTDIR/<name>.webp (1536 x 1024, medium quality, saved as WebP quality 80: about 180 KB). Existing files are skipped, so to
redraw one, move it away first.

Uses the image provider from backend/.env through labbox_cli.image_provider (OpenAI first). The owner approved
OpenAI for covers and these notes only, at medium quality; about $0.04 an image. The key is never printed.

Every page is checked by eye, letter by letter, before it is used: image models misspell words, drop or
repeat a line, and get digits wrong. Redraw a wrong page (or shorten its lines); never ship it.
See COURSE_PRODUCTION.md, "Handwritten notes".
"""
import json
import sys
from io import BytesIO
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "tools"))

from app.config import get_settings  # noqa: E402

import labbox_cli as cli  # noqa: E402

STYLE = ("A top-down photo of one page of a squared school notebook lying on a wooden desk, soft daylight. "
         "Neat, friendly handwritten notes in dark blue ink, large and easy to read, with {doodle} "
         "(no animals, no robots with faces, no logos, never a cup, mug, glass or any drink) and one "
         "yellow highlighter mark. The handwriting must say exactly these lines, with this exact spelling, "
         "punctuation and symbols, one line each, and nothing else written on the page:\n")


SKETCH = ("A tall page of dotted notebook paper, seen flat from above, filling the whole image, white background. "
          "A friendly hand-drawn sketchnote in black felt-tip marker with soft pastel highlighter (yellow, green, "
          "light blue), clean and very easy to read, like a good student's revision page. No photos, no logos, no "
          "people, no animals, never a cup, mug, glass or any drink. Write every text exactly as given, with this "
          "exact spelling, punctuation and symbols, and write nothing else on the page. Layout from top to bottom:\n"
          "1. A big hand-lettered title, underlined with yellow highlighter: {title}\n"
          "2. Under it, smaller, in brackets: ({subtitle})\n"
          "3. A rectangle with a light blue highlighter edge, holding this sentence: {box}\n"
          "4. A row of {n} hand-drawn boxes joined by arrows from left to right, one text per box, in this order: {flow}\n"
          "5. A smaller hand-lettered heading underlined with green highlighter: {list_title}\n"
          "6. A bullet list, each bullet on its own pastel highlighter stripe:\n{bullets}")


def sketch_prompt(sketch: dict) -> str:
    flow = " -> ".join(f'"{step}"' for step in sketch["flow"])
    bullets = "\n".join(f"- {b}" for b in sketch["bullets"])
    return SKETCH.format(title=sketch["title"], subtitle=sketch["subtitle"], box=sketch["box"], n=len(sketch["flow"]),
                         flow=flow, list_title=sketch["list_title"], bullets=bullets)


def main() -> None:
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    jobs, out, doodle = json.loads(Path(sys.argv[1]).read_text()), Path(sys.argv[2]), sys.argv[3]
    out.mkdir(parents=True, exist_ok=True)
    provider = cli.image_provider(get_settings())
    if not provider:
        sys.exit("no image provider configured in backend/.env")
    name, key, model = provider
    for job in jobs:
        target = out / f"{job['name']}.webp"
        if target.exists():
            continue
        if "sketch" in job:
            prompt, size = sketch_prompt(job["sketch"]), "1024x1536"
        else:
            prompt, size = STYLE.format(doodle=doodle) + "\n".join(job["lines"]), "1536x1024"
        try:
            raw = cli.generate_image(prompt, name, key, model, quality="medium", size=size)
            # The provider's file is about 2 MB; WebP quality 80 keeps the handwriting sharp at about 180 KB.
            image = Image.open(BytesIO(raw)).convert("RGB")
            image.save(target, "WEBP", quality=80, method=6)
            print("ok", job["name"], flush=True)
        except Exception as e:  # keep going; the error text never contains the key
            print("fail", job["name"], str(e)[:200], flush=True)


if __name__ == "__main__":
    main()
