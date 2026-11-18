"""Lab covers from the real technology logos, on the technology's own brand colours.

The logos are devicon's "original" SVGs (MIT, see logos/LICENSE-devicon), copied into tools/logos/.
A cover is one SVG, 1200 x 800 (the 3:2 card shape): the brand colour as the background, the main
logo on a white tile, an optional second logo as a small badge (FastAPI on Python, Spring on Java),
and a faint oversized copy of the main logo behind. A pattern seeded from the lab id keeps two labs
on the same technology from looking identical. Logos are trademarks of their owners; they are used
here only to say what a lab teaches.
"""
import hashlib
import math
import random
import re
import xml.etree.ElementTree as ET
from pathlib import Path

LOGOS_DIR = Path(__file__).resolve().parent / "logos"
W, H = 1200, 800

# name: (background, background dark end, accent). Brand colours from each project's own guidelines.
BRANDS: dict[str, tuple[str, str, str]] = {
    "python": ("#3776AB", "#163a5f", "#FFD43B"),
    "java": ("#E76F00", "#7a2d00", "#5382A1"),
    "fastapi": ("#009688", "#003f3a", "#ffffff"),
    "spring": ("#6DB33F", "#24501a", "#ffffff"),
    "postgresql": ("#336791", "#14304a", "#ffffff"),
    "go": ("#00ADD8", "#00506a", "#ffffff"),
    "javascript": ("#F7DF1E", "#b89a00", "#323330"),
    "express": ("#3a3a3a", "#0b0b0b", "#ffffff"),
    "redis": ("#DC382D", "#6e110b", "#ffffff"),
    "nodejs": ("#5FA04E", "#22431b", "#ffffff"),
    "typescript": ("#3178C6", "#13355f", "#ffffff"),
    "linux": ("#3a3a3a", "#0b0b0b", "#FCC624"),
    "git": ("#F05033", "#7d1d0c", "#ffffff"),
    "docker": ("#2496ED", "#0a4578", "#ffffff"),
    "kubernetes": ("#326CE5", "#122f73", "#ffffff"),
    "nginx": ("#009639", "#003f17", "#ffffff"),
    "mysql": ("#00758F", "#003342", "#F29111"),
    "mongodb": ("#47A248", "#12351a", "#ffffff"),
}


def known_logos() -> list[str]:
    return sorted(BRANDS)


def _logo(name: str, prefix: str) -> tuple[str, str]:
    """(viewBox, inner markup) of a logo, with its ids prefixed so two logos never clash."""
    raw = (LOGOS_DIR / f"{name}.svg").read_text(encoding="utf-8")
    view = re.search(r'viewBox="([^"]+)"', raw)
    inner = re.sub(r"^.*?<svg[^>]*>|</svg>\s*$", "", raw.strip(), flags=re.S)
    inner = re.sub(r'id="([^"]+)"', rf'id="{prefix}\1"', inner)
    inner = re.sub(r"url\(#([^)]+)\)", rf"url(#{prefix}\1)", inner)
    inner = re.sub(r'href="#([^"]+)"', rf'href="#{prefix}\1"', inner)
    return (view.group(1) if view else "0 0 128 128"), inner


def build_cover(logos: list[str], seed: str) -> str:
    """The cover SVG for a lab: logos[0] is the main logo, logos[1] (optional) the badge."""
    unknown = [n for n in logos if n not in BRANDS]
    if not logos or unknown or len(logos) > 2:
        raise ValueError(f"Use one or two of: {', '.join(known_logos())}")
    r = random.Random(int(hashlib.sha256(seed.encode()).hexdigest()[:12], 16))
    bg, dark, accent = BRANDS[logos[0]]
    angle = r.randint(20, 70)
    wm_x, wm_y, wm_rot = r.randint(-260, -140), r.randint(260, 380), r.randint(-18, -6)
    glow_x = r.randint(760, 1000)

    defs = [
        f'<linearGradient id="bg" gradientTransform="rotate({angle} .5 .5)">'
        f'<stop offset="0" stop-color="{bg}"/><stop offset="1" stop-color="{dark}"/></linearGradient>',
        '<radialGradient id="glow"><stop offset="0" stop-color="#fff" stop-opacity=".32"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>',
        '<pattern id="dots" width="28" height="28" patternUnits="userSpaceOnUse">'
        '<circle cx="2" cy="2" r="1.6" fill="#fff" fill-opacity=".16"/></pattern>',
        '<filter id="mono"><feFlood flood-color="#fff"/><feComposite in2="SourceAlpha" operator="in"/></filter>',
        '<filter id="shadow" x="-40%" y="-40%" width="180%" height="180%">'
        '<feDropShadow dx="0" dy="26" stdDeviation="30" flood-color="#000" flood-opacity=".38"/></filter>',
    ]
    view0, main = _logo(logos[0], "m-")
    _, watermark = _logo(logos[0], "w-")
    body = [
        f'<rect width="{W}" height="{H}" fill="url(#bg)"/>',
        f'<rect width="{W}" height="{H}" fill="url(#dots)"/>',
        f'<circle cx="{glow_x}" cy="60" r="520" fill="url(#glow)"/>',
        f'<g opacity=".1" filter="url(#mono)" transform="rotate({wm_rot} {wm_x + 330} {wm_y + 330})">'
        f'<svg x="{wm_x}" y="{wm_y}" width="660" height="660" viewBox="{view0}">{watermark}</svg></g>',
    ]
    cx, cy, tile = 600, 390, 320
    for i, rad in enumerate((250, 330)):
        body.append(f'<circle cx="{cx}" cy="{cy}" r="{rad}" fill="none" stroke="#fff" stroke-opacity="{.18 - i * .07:.2f}" stroke-width="2"/>')
    for _ in range(5):  # small accent dots on the orbits
        rad, a = r.choice((250, 330)), r.uniform(0, 6.283)
        body.append(f'<circle cx="{cx + rad * math.cos(a):.0f}" cy="{cy + rad * math.sin(a):.0f}" r="{r.randint(5, 9)}" fill="{accent}" fill-opacity=".9"/>')
    x, y = cx - tile // 2, cy - tile // 2
    body.append(f'<rect x="{x}" y="{y}" width="{tile}" height="{tile}" rx="72" fill="#fff" filter="url(#shadow)"/>')
    pad = 56
    body.append(f'<svg x="{x + pad}" y="{y + pad}" width="{tile - 2 * pad}" height="{tile - 2 * pad}" viewBox="{view0}">{main}</svg>')
    if len(logos) == 2:
        view1, badge = _logo(logos[1], "b-")
        b = 150
        bx, by = x + tile - b + 46, y + tile - b + 46
        body.append(f'<rect x="{bx}" y="{by}" width="{b}" height="{b}" rx="38" fill="#fff" stroke="{dark}" stroke-width="6" filter="url(#shadow)"/>')
        body.append(f'<svg x="{bx + 26}" y="{by + 26}" width="{b - 52}" height="{b - 52}" viewBox="{view1}">{badge}</svg>')
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
        f'<defs>{"".join(defs)}</defs>{"".join(body)}</svg>\n'
    )
    ET.fromstring(svg)  # a browser shows a broken image for invalid XML, so fail here instead
    return svg
