"""Turn the PNGs from tools/home-shots.mjs into the home page's rotating lab screenshots.

    backend/.venv/bin/python frontend/tools/home-shots.py <shots-dir>

Writes frontend/public/images/labs/<name>.webp (1920x1152) and frontend/src/homeShots.json.
"""

import json
import sys
from pathlib import Path

from PIL import Image

src = Path(sys.argv[1])
root = Path(__file__).resolve().parent.parent
out = root / "public" / "images" / "labs"
out.mkdir(parents=True, exist_ok=True)
manifest = json.loads((src / "shots.json").read_text())
shots = []
for name, m in sorted(manifest.items()):
    img = Image.open(src / m["file"]).convert("RGB").resize((1920, 1152), Image.LANCZOS)
    img.save(out / f"{name}.webp", quality=84, method=6)
    shots.append({"src": f"/images/labs/{name}.webp", "caption": m["caption"], "alt": m["alt"]})
(root / "src" / "homeShots.json").write_text(json.dumps(shots, indent=2) + "\n")
print(f"{len(shots)} shots, {sum(p.stat().st_size for p in out.glob('*.webp')) // 1024} KB")
