"""Search Wikimedia Commons for candidate lesson photos.

    python3 tools/authoring/commons_search.py OUT.json "key=search words" ["key2=more words" ...]

Writes OUT.json: key -> up to 8 candidates {title, thumb, w, h, license, artist, desc}. Open the thumbs,
pick one per key, and pass its title to commons_fetch.py. Paced for Commons' rate limits (it answers 429
when asked too fast); a generic user agent, no personal details. See COURSE_PRODUCTION.md, "Photos".
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request

UA = "labbox-lesson-images/1.0 (education; low volume)"


def search(query: str) -> list[dict]:
    params = {"action": "query", "format": "json", "generator": "search", "gsrsearch": f"filetype:bitmap {query}",
              "gsrnamespace": 6, "gsrlimit": 8, "prop": "imageinfo", "iiprop": "url|extmetadata|size",
              "iiurlwidth": 360}
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    data: dict = {}
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            data = json.load(urllib.request.urlopen(req, timeout=30))
            break
        except Exception as e:  # 429 or a network hiccup: wait longer each time
            print("retry", query, e, file=sys.stderr)
            time.sleep(10 * (attempt + 1))
    pages = sorted(data.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0))
    out = []
    for p in pages:
        ii = p["imageinfo"][0]
        md = ii.get("extmetadata", {})

        def meta(name: str) -> str:
            return re.sub("<[^>]+>", "", (md.get(name, {}) or {}).get("value", "")).strip()

        out.append({"title": p["title"], "thumb": ii.get("thumburl"), "w": ii.get("width"), "h": ii.get("height"),
                    "license": meta("LicenseShortName"), "artist": meta("Artist")[:80],
                    "desc": meta("ImageDescription")[:160]})
    return out


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    result = {}
    for arg in sys.argv[2:]:
        key, _, query = arg.partition("=")
        result[key] = search(query or key)
        print(key, len(result[key]), flush=True)
        time.sleep(3)
    with open(sys.argv[1], "w") as f:
        json.dump(result, f, indent=1)


if __name__ == "__main__":
    main()
