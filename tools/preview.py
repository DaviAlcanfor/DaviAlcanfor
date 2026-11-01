"""Render every SVG in assets/ (plus the first cover frame) to PNG and tile them into contact sheets.

    python tools/preview.py [out_dir]
"""
import sys
from pathlib import Path

import resvg_py
from PIL import Image

ROOT = Path(__file__).parent.parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "tools" / "out" / "preview"


def render(path):
    png = OUT / f"{path.stem}.png"
    png.write_bytes(bytes(resvg_py.svg_to_bytes(svg_path=str(path))))
    return png


def sheet(paths, name, cols):
    ims = [Image.open(p).convert("RGB") for p in paths]
    cell_w = max(i.width for i in ims)
    rows = [ims[k:k + cols] for k in range(0, len(ims), cols)]
    canvas = Image.new("RGB", (cell_w * cols + 20 * (cols + 1),
                               sum(max(i.height for i in r) + 20 for r in rows) + 20), (60, 60, 60))
    y = 20
    for r in rows:
        x = 20
        for im in r:
            canvas.paste(im, (x, y))
            x += im.width + 20
        y += max(i.height for i in r) + 20
    canvas.save(OUT / name)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    svgs = {p.stem: render(p) for p in sorted((ROOT / "assets").glob("*.svg"))}
    Image.open(ROOT / "assets" / "cover.gif").convert("RGB").save(OUT / "cover.png")
    pick = lambda prefix: [v for k, v in svgs.items() if k.startswith(prefix)]
    sheet([OUT / "cover.png", svgs["intro"], *pick("divider"), *pick("header"), svgs["footer"]], "sheet-page.png", 1)
    sheet(pick("link") + pick("relic"), "sheet-badges.png", 4)
    sheet(pick("item") + pick("votive"), "sheet-cards.png", 3)
    print(OUT)


if __name__ == "__main__":
    main()
