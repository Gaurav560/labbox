"""Insert :::photo blocks into chapter files.

    python3 tools/authoring/insert_photos.py labs/<lab>/chapters photos.json

photos.json is a list of {chapter, step, lead, src, alt, credit, license, source, caption}:
- chapter: the file's number prefix ("07" for 07-tools.md);
- step: the exact title of the step the photo goes in;
- lead: the sentence that introduces the photo (it says why the learner is looking at it);
- the rest fill the directive; caption is its one line.

The lead and the photo go at the end of the step, or just before its :::mission when it has one. A photo
whose src is already in the chapter is skipped, so the script can run twice. Read the result: the photo
often reads better right after the paragraph it belongs to. See COURSE_PRODUCTION.md, "Photos".
"""
import glob
import json
import os
import sys


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    chapters, items = sys.argv[1], json.load(open(sys.argv[2]))
    for it in items:
        path = glob.glob(os.path.join(chapters, it["chapter"] + "-*.md"))[0]
        s = open(path).read()
        if it["src"] in s:
            print("skip", path)
            continue
        i = s.index(f'title="{it["step"]}"')
        j = s.find("\n:::step{", i)
        j = len(s) if j < 0 else j
        block = (f':::photo{{src="{it["src"]}" alt="{it["alt"]}" credit="{it["credit"]}" license="{it["license"]}" '
                 f'source="{it["source"]}"}}\n{it["caption"]}\n:::')
        m = s.find("\n:::mission", i, j)
        k = m if m >= 0 else s.rindex("\n:::\n", i, j + 1)
        s = s[:k] + "\n\n" + it["lead"] + "\n\n" + block + s[k:]
        open(path, "w").write(s)
        print("ok", path, it["step"])


if __name__ == "__main__":
    main()
