"""Lab covers from the real technology logos, on the technology's own brand colours.

The logos are devicon's "original" SVGs (MIT, see logos/LICENSE-devicon) plus Duke, the Java mascot
(BSD, see logos/LICENSE-duke), copied into tools/logos/.
A cover is one SVG, 1200 x 800 (the 3:2 card shape): the brand colour as the background and the
main logo as the picture, big and in its own colours on a soft light, plus an optional second logo
as a small badge (Python on FastAPI, Java on Spring). A pattern seeded from the lab id keeps two labs
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
    "java": ("#1b4f80", "#08172b", "#f89820"),  # Java blue: the red flame and blue cup both stand out
    "duke-waving": ("#f89820", "#b3460a", "#ffffff"),  # Duke, the Java mascot (BSD, see logos/LICENSE-duke)
    "duke-thumbsup": ("#1b4f80", "#08172b", "#f89820"),
    "fastapi": ("#009688", "#003f3a", "#ffffff"),
    "spring": ("#6DB33F", "#24501a", "#ffffff"),
    "spring-ai": ("#2d5a1b", "#0f2408", "#7eb050"),  # the Spring AI brain-and-leaf mark, on a deep green
    "langchain4j": ("#2f6b3a", "#0e2614", "#f5a623"),  # LangChain4j's parrot (its own logo, Apache 2.0 repository), on a deep green
    "langchain": ("#1C3C3C", "#0a1a1a", "#4fd1a5"),  # the LangChain mark (Simple Icons, CC0), on its own dark teal
    "postgresql": ("#336791", "#14304a", "#ffffff"),
    "sql": ("#4338ca", "#1e1b4b", "#f59e0b"),  # our own generic SQL mark, amber on indigo
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


# The light behind the logo, when white is not the best match for a brand.
SPOTS: dict[str, str] = {}


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
    bg, dark, _accent = BRANDS[logos[0]]
    spot = SPOTS.get(logos[0], "#fff")
    angle = r.randint(20, 70)
    glow_x = r.randint(760, 1000)

    defs = [
        f'<linearGradient id="bg" gradientTransform="rotate({angle} .5 .5)">'
        f'<stop offset="0" stop-color="{bg}"/><stop offset="1" stop-color="{dark}"/></linearGradient>',
        '<radialGradient id="glow"><stop offset="0" stop-color="#fff" stop-opacity=".32"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>',
        f'<radialGradient id="spot"><stop offset="0" stop-color="{spot}" stop-opacity=".92"/>'
        f'<stop offset=".55" stop-color="{spot}" stop-opacity=".55"/><stop offset="1" stop-color="{spot}" stop-opacity="0"/></radialGradient>',
        '<filter id="shadow" x="-40%" y="-40%" width="180%" height="180%">'
        '<feDropShadow dx="0" dy="18" stdDeviation="22" flood-color="#000" flood-opacity=".28"/></filter>',
    ]
    view0, main = _logo(logos[0], "m-")
    cx, cy, size = 600, 400, 540  # the logo is the picture: big, in the middle, in its own colours
    body = [
        f'<rect width="{W}" height="{H}" fill="url(#bg)"/>',
        f'<circle cx="{glow_x}" cy="40" r="520" fill="url(#glow)"/>',
        # a soft light behind the logo, so a red logo still stands out on a red card
        f'<circle cx="{cx}" cy="{cy}" r="400" fill="url(#spot)"/>',
    ]
    for i, rad in enumerate((350, 430)):
        body.append(f'<circle cx="{cx}" cy="{cy}" r="{rad}" fill="none" stroke="#fff" stroke-opacity="{.22 - i * .09:.2f}" stroke-width="2"/>')
    body.append(f'<g filter="url(#shadow)"><svg x="{cx - size // 2}" y="{cy - size // 2}" width="{size}" height="{size}" viewBox="{view0}">{main}</svg></g>')
    if len(logos) == 2:
        view1, badge = _logo(logos[1], "b-")
        b = 170
        bx, by = cx + size // 2 - b + 40, cy + size // 2 - b + 10
        body.append(f'<rect x="{bx}" y="{by}" width="{b}" height="{b}" rx="44" fill="#fff" stroke="{dark}" stroke-width="6" filter="url(#shadow)"/>')
        body.append(f'<svg x="{bx + 30}" y="{by + 30}" width="{b - 60}" height="{b - 60}" viewBox="{view1}">{badge}</svg>')
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
        f'<defs>{"".join(defs)}</defs>{"".join(body)}</svg>\n'
    )
    ET.fromstring(svg)  # a browser shows a broken image for invalid XML, so fail here instead
    return svg
