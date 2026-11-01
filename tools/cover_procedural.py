"""Procedural pixel-art cover: a penitent kneeling before a candlelit altar.

Everything is drawn in code on a 240x80 canvas, lit, quantized to the
design-system palette with ordered dithering, and upscaled 4x into a GIF.
"""
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)

W, H = 240, 80
SCALE = 4
FRAMES = 24
FRAME_MS = 110
FLOOR_Y = 66

PALETTE = {
    "void": "#0E0B0A",
    "shadow": "#1A1412",
    "cloak": "#241A18",
    "cloak_lit": "#3A2A26",
    "stone_dark": "#2A2220",
    "stone": "#3B312D",
    "stone_lit": "#5A4A40",
    "steel": "#4E5B57",
    "parchment": "#8C7F68",
    "bone": "#D8CBB0",
    "blood": "#6E1414",
    "crimson": "#A3241C",
    "gold": "#B08A3E",
    "gold_light": "#E0B860",
    "flame": "#F4E2B0",
}


def hex_rgb(value):
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))


PAL_NAMES = list(PALETTE)
PAL_RGB = np.array([hex_rgb(PALETTE[n]) for n in PAL_NAMES], dtype=float)
IDX = {name: i for i, name in enumerate(PAL_NAMES)}

BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 - 0.5

ALTAR_CANDLES = [(154, 10), (159, 6), (164, 8), (192, 7), (197, 11), (202, 5)]
FLOOR_CANDLES = [(92, 6), (98, 9), (216, 8), (223, 5)]
FIG_DX = 24


def candle_tops():
    tops = [(x, 52 - h) for x, h in ALTAR_CANDLES]
    tops += [(x, FLOOR_Y - h) for x, h in FLOOR_CANDLES]
    return tops


def draw_background(d):
    for y in range(H):
        d.line([(0, y), (W, y)], fill=IDX["void"])
    # side arches, barely visible
    for cx in (40, 100):
        d.rectangle([cx - 12, 14, cx + 12, FLOOR_Y], fill=IDX["shadow"])
        d.pieslice([cx - 12, 2, cx + 12, 26], 180, 360, fill=IDX["shadow"])
    # left pillar with a hanging chain
    d.rectangle([52, 0, 62, FLOOR_Y], fill=IDX["stone_dark"])
    d.rectangle([50, 58, 64, FLOOR_Y], fill=IDX["stone"])
    d.line([(63, 0), (63, FLOOR_Y)], fill=IDX["stone"])
    d.line([(76, 0), (76, 24)], fill=IDX["stone"])
    d.rectangle([74, 24, 78, 28], outline=IDX["gold"])
    # central stained-glass window behind the altar
    d.rectangle([162, 14, 194, 52], fill=IDX["stone_dark"])
    d.pieslice([162, 0, 194, 30], 180, 360, fill=IDX["stone_dark"])
    d.rectangle([165, 15, 191, 52], fill=IDX["blood"])
    d.pieslice([165, 3, 191, 28], 180, 360, fill=IDX["blood"])
    d.rectangle([170, 20, 186, 48], fill=IDX["crimson"])
    d.pieslice([170, 10, 186, 30], 180, 360, fill=IDX["crimson"])
    for x in (173, 183):
        d.line([(x, 8), (x, 52)], fill=IDX["stone_dark"])
    d.line([(165, 32), (191, 32)], fill=IDX["stone_dark"])


def draw_thorn_wreath(d):
    cx, cy, r = 178, 22, 7
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=IDX["shadow"])
    d.ellipse([cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1], outline=IDX["stone_dark"])
    for k in range(12):
        a = 2 * math.pi * k / 12
        x0, y0 = cx + math.cos(a) * r, cy + math.sin(a) * r
        x1, y1 = cx + math.cos(a) * (r + 3), cy + math.sin(a) * (r + 3)
        d.line([(x0, y0), (x1, y1)], fill=IDX["shadow"])
    d.line([(cx, 0), (cx, cy - r)], fill=IDX["shadow"])


def draw_floor(d):
    d.rectangle([0, FLOOR_Y, W, H], fill=IDX["stone_dark"])
    for y in (FLOOR_Y, 71, 76):
        d.line([(0, y), (W, y)], fill=IDX["shadow"])
    rng = random.Random(7)
    for y0, y1 in ((FLOOR_Y, 71), (71, 76), (76, H)):
        x = rng.randint(0, 20)
        while x < W:
            d.line([(x, y0), (x, y1)], fill=IDX["shadow"])
            x += rng.randint(18, 30)


def draw_altar(d):
    d.rectangle([148, 52, 208, FLOOR_Y], fill=IDX["stone"])
    d.rectangle([146, 50, 210, 52], fill=IDX["stone_lit"])
    d.line([(146, 50), (210, 50)], fill=IDX["gold"])
    d.rectangle([150, 56, 206, FLOOR_Y], outline=IDX["stone_dark"])
    # crimson altar cloth with a pointed hem
    d.polygon([(170, 52), (186, 52), (186, 60), (178, 64), (170, 60)], fill=IDX["crimson"])
    d.line([(170, 52), (170, 60)], fill=IDX["blood"])
    d.line([(178, 64), (186, 60)], fill=IDX["blood"])
    d.point((178, 58), fill=IDX["gold_light"])


def draw_candles(d):
    for x, h in ALTAR_CANDLES:
        d.rectangle([x, 52 - h, x + 1, 51], fill=IDX["bone"])
        d.point((x + 1, 52 - h + 2), fill=IDX["parchment"])
    for x, h in FLOOR_CANDLES:
        d.rectangle([x, FLOOR_Y - h, x + 1, FLOOR_Y - 1], fill=IDX["bone"])
        d.rectangle([x - 1, FLOOR_Y - 2, x + 2, FLOOR_Y - 1], fill=IDX["parchment"])


def penitent_layer():
    """Kneeling hooded figure facing the altar, hands on a planted sword.

    Returns (index layer, mask) drawn on its own canvas so lighting and
    dithering never swallow the silhouette.
    """
    dx = FIG_DX
    layer = Image.new("P", (W, H), 0)
    mask_img = Image.new("L", (W, H), 0)
    d, md = ImageDraw.Draw(layer), ImageDraw.Draw(mask_img)

    def shift(points):
        return [(x + dx, y) for x, y in points]

    body = shift([(80, 66), (82, 52), (86, 42), (90, 36), (100, 36), (104, 44),
                  (106, 52), (112, 57), (117, 61), (118, 66)])
    arm = shift([(102, 42), (110, 41), (116, 41), (116, 46), (108, 47), (103, 48)])
    hood = [89 + dx, 26, 101 + dx, 39]
    for draw in (d, md):
        fill = IDX["cloak"] if draw is d else 1
        draw.ellipse(hood, fill=fill)
        draw.polygon(body, fill=fill)
        draw.polygon(arm, fill=fill)
    # cloth folds
    for x0, y0, x1, y1 in ((88, 44, 85, 64), (94, 42, 92, 64), (104, 54, 108, 64)):
        d.line([(x0 + dx, y0), (x1 + dx, y1)], fill=IDX["shadow"])
    d.line([(91 + dx, 28), (96 + dx, 27)], fill=IDX["cloak_lit"])
    # face opening inside the hood
    d.polygon(shift([(98, 30), (101, 31), (101, 36), (97, 35)]), fill=IDX["void"])
    # gloved hands
    d.rectangle([116 + dx, 42, 120 + dx, 45], fill=IDX["blood"])
    md.rectangle([116 + dx, 42, 120 + dx, 45], fill=1)

    idx, mask = np.array(layer), np.array(mask_img)
    edge = (mask == 1) & (np.roll(mask, -1, axis=1) == 0)
    edge2 = (mask == 1) & (np.roll(mask, -2, axis=1) == 0) & ~edge
    back = (mask == 1) & (np.roll(mask, 1, axis=1) == 0)
    top = (mask == 1) & (np.roll(mask, 1, axis=0) == 0)
    idx[edge2 & (idx == IDX["cloak"])] = IDX["blood"]
    idx[edge] = IDX["crimson"]
    idx[(back | top) & (idx == IDX["cloak"])] = IDX["cloak_lit"]
    return idx, mask


def draw_sword(idx):
    x = 121 + FIG_DX
    idx[47:66, x] = IDX["steel"]
    idx[47:65, x + 1] = IDX["stone_lit"]
    idx[46, x - 3:x + 5] = IDX["gold"]
    idx[41:46, x] = IDX["blood"]
    idx[40, x] = IDX["gold_light"]
    idx[42:46, x - 5:x] = IDX["blood"]


def build_base():
    img = Image.new("P", (W, H), IDX["void"])
    d = ImageDraw.Draw(img)
    draw_background(d)
    draw_thorn_wreath(d)
    draw_floor(d)
    draw_altar(d)
    draw_candles(d)
    return np.array(img)


def light_map(frame, tops=None):
    yy, xx = np.mgrid[0:H, 0:W]
    light = np.zeros((H, W))
    for i, (x, y) in enumerate(tops or candle_tops()):
        flicker = 1 + 0.18 * math.sin(2 * math.pi * (frame / FRAMES * (2 + i % 3) + i * 0.37))
        dist = np.hypot(xx - x, (yy - y) * 1.3)
        light += 0.55 * flicker * np.clip(1 - dist / 30, 0, 1) ** 2
    return np.clip(light, 0, 1.2)


def vignette():
    yy, xx = np.mgrid[0:H, 0:W]
    dx = (xx - W * 0.6) / (W * 0.6)
    dy = (yy - H * 0.55) / (H * 0.8)
    return np.clip(1 - 0.75 * (dx ** 2 + dy ** 2), 0.2, 1)


def quantize(rgb):
    h, w, _ = rgb.shape
    noise = np.tile(BAYER4, (h // 4 + 1, w // 4 + 1))[:h, :w][..., None] * 28
    flat = (rgb + noise).reshape(-1, 1, 3)
    dists = ((flat - PAL_RGB[None]) ** 2).sum(-1)
    return dists.argmin(1).reshape(h, w)


def draw_flames(idx, frame, tops=None):
    for i, (x, y) in enumerate(tops or candle_tops()):
        sway = int(round(math.sin(2 * math.pi * (frame / FRAMES * 3 + i * 0.5)) * 0.6))
        tall = 1 if (frame + i) % 5 else 0
        idx[y - 1, x] = IDX["flame"]
        idx[y - 2, x + sway] = IDX["gold_light"]
        if tall:
            idx[y - 3, x + sway] = IDX["gold"]


def ember_particles(seed=3, count=36, tops=None):
    rng = random.Random(seed)
    tops = tops or candle_tops()
    return [
        {
            "x": tops[i % len(tops)][0] + rng.uniform(-2, 2),
            "y": tops[i % len(tops)][1] - 2,
            "phase": rng.random(),
            "rise": rng.uniform(18, 34),
            "amp": rng.uniform(1, 3.5),
            "waves": rng.choice((1, 2)),
        }
        for i in range(count)
    ]


def draw_embers(idx, frame, particles):
    for p in particles:
        t = (frame / FRAMES + p["phase"]) % 1
        if t > 0.85:
            continue
        x = int(round(p["x"] + math.sin(2 * math.pi * (t * p["waves"] + p["phase"])) * p["amp"]))
        y = int(round(p["y"] - t * p["rise"]))
        if 0 <= x < W and 0 <= y < H:
            idx[y, x] = IDX["gold_light"] if t < 0.3 else IDX["crimson"] if t < 0.6 else IDX["blood"]


def render_frame(base, frame, particles, figure):
    rgb = PAL_RGB[base].copy()
    lit = light_map(frame)[..., None]
    rgb = rgb * (0.55 + lit) + lit * np.array([90, 40, 10])
    rgb *= vignette()[..., None]
    idx = quantize(np.clip(rgb, 0, 255))
    fig_idx, fig_mask = figure
    idx[fig_mask == 1] = fig_idx[fig_mask == 1]
    draw_sword(idx)
    draw_flames(idx, frame)
    draw_embers(idx, frame, particles)
    return idx


def to_image(idx):
    flat_pal = [int(c) for rgb in PAL_RGB for c in rgb]
    img = Image.fromarray(idx.astype(np.uint8), mode="P")
    img.putpalette(flat_pal + [0] * (768 - len(flat_pal)))
    return img.resize((W * SCALE, H * SCALE), Image.NEAREST)


def main():
    base = build_base()
    particles = ember_particles()
    figure = penitent_layer()
    frames = [to_image(render_frame(base, f, particles, figure)) for f in range(FRAMES)]
    frames[0].save(OUT / "cover_procedural.png")
    frames[0].save(OUT / "cover_procedural.gif", save_all=True, append_images=frames[1:],
                   duration=FRAME_MS, loop=0, optimize=False, disposal=1)
    print("ok", (OUT / "cover_procedural.gif").stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
