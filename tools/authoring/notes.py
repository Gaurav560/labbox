"""Draw the handwritten-notes page for chapter recaps (an AI image, one per recap).

    cd backend && .venv/bin/python ../tools/authoring/notes.py JOBS.json OUTDIR "a small doodle of ..."

JOBS.json is a list of {name, lines}: name like "springai-07-notes", lines the five or six short lines the
page must say. Writes OUTDIR/<name>.webp (1536 x 1024, medium quality, saved as WebP quality 80: about 180 KB). Existing files are skipped, so to
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
        prompt = STYLE.format(doodle=doodle) + "\n".join(job["lines"])
        try:
            raw = cli.generate_image(prompt, name, key, model, quality="medium")
            # The provider's file is about 2 MB; WebP quality 80 keeps the handwriting sharp at about 180 KB.
            image = Image.open(BytesIO(raw)).convert("RGB")
            image.save(target, "WEBP", quality=80, method=6)
            print("ok", job["name"], flush=True)
        except Exception as e:  # keep going; the error text never contains the key
            print("fail", job["name"], str(e)[:200], flush=True)


if __name__ == "__main__":
    main()
