"""Draws the topographic contour pattern behind the home page: frontend/public/patterns/topo.svg.

A smooth made-up terrain (a few hills and valleys plus gentle waves) is cut at even heights with
marching squares; each cut is one contour line. Pure Python, deterministic: run it again and you get
the same file. The lines are black on transparent; the page colours them with a CSS mask.

    python3 tools/make_topo.py
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "frontend" / "public" / "patterns" / "topo.svg"
W, H, CELL = 1920, 1200, 8
LEVELS = 22

HILLS = [  # x, y (0..1), height, spread
    (0.18, 0.28, 1.0, 0.16), (0.72, 0.22, 0.85, 0.20), (0.55, 0.78, 1.1, 0.18),
    (0.08, 0.85, 0.6, 0.14), (0.95, 0.70, 0.7, 0.15), (0.40, 0.45, -0.55, 0.12),
]


def height(x: float, y: float) -> float:
    h = 0.0
    for hx, hy, a, s in HILLS:
        d2 = ((x - hx) * 1.6) ** 2 + (y - hy) ** 2
        h += a * math.exp(-d2 / (2 * s * s))
    h += 0.12 * math.sin(x * 7.1 + y * 2.3) + 0.08 * math.sin(y * 9.4 - x * 3.7)
    return h


def contours() -> list[list[tuple[float, float]]]:
    nx, ny = W // CELL, H // CELL
    f = [[height(i / nx, j / ny) for i in range(nx + 1)] for j in range(ny + 1)]
    lo = min(min(r) for r in f)
    hi = max(max(r) for r in f)
    lines = []
    for k in range(1, LEVELS):
        level = lo + (hi - lo) * k / LEVELS
        segs = []
        for j in range(ny):
            for i in range(nx):
                corners = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
                vals = [f[cy][cx] for cx, cy in corners]
                pts = []
                for e in range(4):
                    (ax, ay), (bx, by) = corners[e], corners[(e + 1) % 4]
                    va, vb = vals[e], vals[(e + 1) % 4]
                    if (va < level) != (vb < level):
                        t = (level - va) / (vb - va)
                        pts.append((round((ax + (bx - ax) * t) * CELL, 1), round((ay + (by - ay) * t) * CELL, 1)))
                if len(pts) == 2:
                    segs.append((pts[0], pts[1]))
                elif len(pts) == 4:  # saddle: pair the crossings in order
                    segs += [(pts[0], pts[1]), (pts[2], pts[3])]
        lines += _join(segs)
    return [ln for ln in lines if len(ln) > 6]


def _join(segs):
    """Chain segments that share end points into polylines."""
    ends: dict[tuple, list[int]] = {}
    for n, (a, b) in enumerate(segs):
        ends.setdefault(a, []).append(n)
        ends.setdefault(b, []).append(n)
    used = [False] * len(segs)
    out = []
    for n in range(len(segs)):
        if used[n]:
            continue
        used[n] = True
        line = list(segs[n])
        for forward in (True, False):
            while True:
                tip = line[-1] if forward else line[0]
                nxt = next((m for m in ends.get(tip, []) if not used[m]), None)
                if nxt is None:
                    break
                used[nxt] = True
                a, b = segs[nxt]
                p = b if a == tip else a
                line.append(p) if forward else line.insert(0, p)
        out.append(line)
    return out


def main() -> None:
    paths = []
    for ln in contours():
        ln = ln[::2] + ([ln[-1]] if len(ln) % 2 == 0 else [])  # every other point is plenty
        d = "M" + " L".join(f"{x:g} {y:g}" for x, y in ln)
        paths.append(f'<path d="{d}"/>')
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">'
        f'<g fill="none" stroke="#000" stroke-width="1.2" stroke-linejoin="round">{"".join(paths)}</g></svg>\n'
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg)
    print(f"{OUT} ({len(svg) // 1024} KB, {len(paths)} lines)")


if __name__ == "__main__":
    main()
