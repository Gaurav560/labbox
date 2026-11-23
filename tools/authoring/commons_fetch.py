"""Download chosen Wikimedia Commons photos as lesson-ready WebP files, with their credits.

    python3 tools/authoring/commons_fetch.py OUTDIR "name=File:Some photo.jpg" ["name2=File:..." ...]

For each pair: asks Commons for a thumbnail at most 1000 px wide (originals are rate-limited), turns it into
OUTDIR/<name>.webp (RGB, quality 82; a tall photo is cropped to a square, keeping its upper part), and adds
its title, license, artist, source page and description to OUTDIR/credits.json. Files already there are
skipped, so a run can be repeated after a 429. Set W=800 to ask for a narrower thumbnail.

Check every license (CC BY, CC BY-SA, CC0 or public domain only) and write the credit and source into the
:::photo directive. credits.json is a working file: keep it out of frontend/public. See COURSE_PRODUCTION.md, "Photos".
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from io import BytesIO

from PIL import Image

UA = "labbox-lesson-images/1.0 (education; low volume)"


def api(title: str, params: dict) -> dict:
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {"action": "query", "format": "json", "titles": title, "prop": "imageinfo", **params})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return list(json.load(urllib.request.urlopen(req, timeout=30))["query"]["pages"].values())[0]


def fetch(out: str, name: str, title: str, credits: dict) -> None:
    if os.path.exists(f"{out}/{name}.webp"):
        print(name, "already there")
        return
    try:
        width = api(title, {"iiprop": "size"})["imageinfo"][0]["width"]
        page = api(title, {"iiprop": "url|extmetadata|size",
                           "iiurlwidth": int(os.environ.get("W", 0)) or min(1000, width - 20)})
    except Exception as e:
        print("MISSING", name, title, e)
        time.sleep(5)
        return
    ii = page["imageinfo"][0]
    md = ii.get("extmetadata", {})

    def meta(key: str) -> str:
        return re.sub("<[^>]+>", "", (md.get(key, {}) or {}).get("value", "")).strip()

    raw = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(ii["thumburl"], headers={"User-Agent": UA})
            raw = urllib.request.urlopen(req, timeout=60).read()
            break
        except Exception as e:
            print(name, "retry", e, file=sys.stderr)
            time.sleep(20 * (attempt + 1))
    if raw is None:
        print("SKIPPED", name)
        return
    im = Image.open(BytesIO(raw)).convert("RGB")
    if im.width > 1000:
        im = im.resize((1000, round(im.height * 1000 / im.width)))
    if im.height > im.width * 1.05:
        top = int((im.height - im.width) * 0.3)
        im = im.crop((0, top, im.width, top + im.width))
    im.save(f"{out}/{name}.webp", "WEBP", quality=82)
    credits[name] = {"title": page["title"], "license": meta("LicenseShortName"), "artist": meta("Artist")[:120],
                     "source": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(page["title"].replace(" ", "_")),
                     "desc": meta("ImageDescription")[:200], "size": f"{im.width}x{im.height}"}
    print(name, im.size, credits[name]["license"], flush=True)


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    path = f"{out}/credits.json"
    credits = json.load(open(path)) if os.path.exists(path) else {}
    for arg in sys.argv[2:]:
        name, _, title = arg.partition("=")
        fetch(out, name, title, credits)
        with open(path, "w") as f:
            json.dump(credits, f, indent=1)
        time.sleep(6)


if __name__ == "__main__":
    main()
