"""Regenerate the terminal README assets (README.md), styled after alcanfor.vercel.app.

Amber on black, Martian Mono, terminal metaphors. Colors come from TERM below, copied from
the site's global.css and Terminal.astro. Text in SVGs is converted to paths (GitHub blocks
external fonts in <img>); animation is CSS only. Output is deterministic.

    python build_terminal.py
"""
import random
import re
from html import escape
from pathlib import Path

import numpy as np
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image, ImageDraw, ImageFont

from build_assets import rect, text

ROOT = Path(__file__).parent
OUT = ROOT / "assets" / "terminal"
FONT_PATH = ROOT / "tools" / "fonts" / "MartianMono.ttf"

# site tokens: --fg, --fg-hi, --fg-dim (55% amber over black) and the projects terminal greys
TERM = {
    "black": "#000000",
    "window": "#0B0B0B",
    "bar": "#151515",
    "border": "#2A2A2A",
    "muted": "#666666",
    "dim": "#A39D90",
    "amber_dim": "#8C6415",
    "amber": "#FFB627",
    "amber_hi": "#FFD27A",
}
T = TERM

MONO = instantiateVariableFont(TTFont(FONT_PATH), {"wght": 400, "wdth": 112.5})
MONO_BOLD = instantiateVariableFont(TTFont(FONT_PATH), {"wght": 600, "wdth": 112.5})

ROLES = ["ai engineer", "data scientist", "ml engineer"]  # SITE.roles
BIO = ["I build AI products end to end:", "LLM agents, ML & deep learning models,", "obsessing over quality at every step."]
GLYPHS = "01<>/\\{}[]=+*#$%&@?!:;~^|ABCDEFXYZ"


def hex_rgb(value):
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))


# ── cover ────────────────────────────────────────────────────────────────

W, H = 840, 300
FPS, SECONDS = 10, 9  # one role every 3s, like the site
FRAMES = FPS * SECONDS
COVER_TONES = ["black", "bar", "border", "muted", "dim", "amber_dim", "amber", "amber_hi"]
NAME = "davi alcanfôr"
STEP = 12  # rain grid: one glyph per 12px cell
NAME_BOX = (130, 92, 710, 176)  # kept clear of rain so the name reads


def pil_font(size, weight):
    font = ImageFont.truetype(str(FONT_PATH), size)
    font.set_variation_by_axes([weight, 112.5])
    return font


def quantize(rgb, tones):
    pal = np.array([hex_rgb(T[t]) for t in tones], float)
    flat = rgb.reshape(-1, 1, 3).astype(float)
    return ((flat - pal[None]) ** 2).sum(-1).argmin(1).reshape(rgb.shape[:2])


def in_name_box(x, y):
    x0, y0, x1, y1 = NAME_BOX
    return x0 <= x <= x1 and y0 <= y <= y1


def static_rain(d, font, rng):
    """Still grey glyph columns in the background, like the site's video backdrop."""
    for x in range(4, W, STEP):
        y = rng.randrange(-200, 0)
        while y < H - 70:
            run = rng.randint(3, 14)
            tone = rng.choice(("bar", "border", "border", "muted"))
            for k in range(run):
                gy = y + k * STEP
                if 0 <= gy < H - 70 and not in_name_box(x, gy):
                    d.text((x, gy), rng.choice(GLYPHS), font=font, fill=hex_rgb(T[tone]))
            y += (run + rng.randint(2, 10)) * STEP


def rain_drops(rng):
    """Falling amber glyph streams; each loops a whole number of times per GIF loop."""
    return [{"x": x, "trail": rng.randint(5, 10), "laps": rng.choice((1, 2)), "phase": rng.random(),
             "seed": rng.randrange(10 ** 6)} for x in rng.sample(range(4, W, STEP), 26)]


def draw_rain(d, frame, drops, font):
    for p in drops:
        span = H + p["trail"] * STEP
        head = (p["phase"] + frame / FRAMES * p["laps"]) % 1 * span
        glyph_rng = random.Random(p["seed"] + frame // 2)  # glyphs mutate every other frame
        for k in range(p["trail"]):
            y = int((head - k * STEP) // STEP * STEP)
            if not 0 <= y < H - 70 or in_name_box(p["x"], y):
                continue
            tone = "amber_hi" if k == 0 else "amber" if k < 3 else "amber_dim" if k < 6 else "border"
            d.text((p["x"], y), glyph_rng.choice(GLYPHS), font=font, fill=hex_rgb(T[tone]))


def scrambled(word, progress, rng):
    """Site scramble: letters resolve left to right; the rest are random glyphs in --fg-dim."""
    done = int(len(word) * progress)
    return [(ch, "amber") if i < done or ch == " " else (rng.choice(GLYPHS), "amber_dim")
            for i, ch in enumerate(word)]


def draw_chars(d, chars, x, y, font):
    for ch, tone in chars:
        d.text((x, y), ch, font=font, fill=hex_rgb(T[tone]))
        x += font.getlength(ch)
    return x


def draw_name(d, frame, font):
    """The name decodes once per loop, then holds."""
    width = font.getlength(NAME)
    chars = scrambled(NAME, min(1, frame / 14), random.Random(frame + 99))
    draw_chars(d, [(c, "amber_hi" if t == "amber" else t) for c, t in chars], (W - width) / 2, 108, font)


def draw_role(d, frame, font):
    per_role = FRAMES // len(ROLES)
    role, t = ROLES[frame // per_role], frame % per_role
    x = draw_chars(d, scrambled(role, min(1, t / 8), random.Random(frame)), 32, 246, font)
    if (frame // 5) % 2 == 0:  # caret blinks once per second
        d.rectangle([x + 4, 250, x + 14, 270], fill=hex_rgb(T["amber"]))


def draw_bio(d, font):
    for i, line in enumerate(BIO):
        d.text((W - 28, 238 + i * 17), line, font=font, fill=hex_rgb(T["amber_dim"]), anchor="ra")


def glitch(rgb, frame):
    """A few torn horizontal slices right when the role changes."""
    per_role = FRAMES // len(ROLES)
    if frame % per_role not in (0, 1):
        return rgb
    rng = random.Random(frame * 7)
    out = rgb.copy()
    for _ in range(4):
        y = rng.randrange(80, 190)
        h = rng.randint(3, 10)
        out[y:y + h] = np.roll(out[y:y + h], rng.choice((-1, 1)) * rng.randint(6, 18), axis=1)
    return out


def build_cover():
    """Procedural: the site's hero (matrix rain, scrambling role, bio) without any photo."""
    pal = np.array([hex_rgb(T[t]) for t in COVER_TONES], np.uint8)
    rain_font, name_font = pil_font(10, 400), pil_font(48, 400)
    role_font, bio_font = pil_font(22, 400), pil_font(10, 400)
    backdrop = Image.new("RGB", (W, H), hex_rgb(T["black"]))
    static_rain(ImageDraw.Draw(backdrop), rain_font, random.Random(5))
    drops = rain_drops(random.Random(11))
    frames = []
    for f in range(FRAMES):
        img = backdrop.copy()
        d = ImageDraw.Draw(img)
        draw_rain(d, f, drops, rain_font)
        draw_name(d, f, name_font)
        draw_role(d, f, role_font)
        draw_bio(d, bio_font)
        # snap anti-aliased text back onto the tones so the GIF palette stays tiny
        idx = quantize(glitch(np.asarray(img), f), COVER_TONES)
        frames.append(Image.fromarray(pal[idx]))
    frames[0].save(OUT / "cover.gif", save_all=True, append_images=frames[1:], duration=1000 // FPS,
                   loop=0, optimize=True, disposal=1)


# ── svg primitives ───────────────────────────────────────────────────────

PAGE_W = 720
UPEM = MONO["head"].unitsPerEm
ADV = MONO["hmtx"]["M"][0] / UPEM  # monospace advance per 1px of font size


def cw(size):
    return ADV * size


def svg(name, w, h, body, title, style="", bg="black"):
    alt = f"<title>{escape(title)}</title>" if title else ""
    role = f'role="img" aria-label="{escape(title)}"' if title else 'aria-hidden="true"'
    css = f"<style>{style}</style>" if style else ""
    (OUT / name).write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" {role}>'
        f"{alt}{css}{rect(0, 0, w, h, T[bg]) if bg else ''}{body}</svg>\n", encoding="utf-8")


# ── stack ────────────────────────────────────────────────────────────────

# only what defines the work; the full list lives in the README's expandable section
STACK = [["python", "rust", "go"], ["langgraph", "pytorch"], ["fastapi", "postgres", "docker"]]
ICON_DIR = ROOT / "tools" / "icons"  # Simple Icons 16.36.0 (CC0), filled 24x24 marks
ICON_FILE = {"postgres": "postgresql"}
TILE, TILE_GAP, GROUP_GAP = 40, 6, 16  # tiles match the 40px link plaques above them


def icon(name, cx, cy, size=20):
    """The tech's mark in amber, centered on (cx, cy)."""
    d = re.search(r' d="([^"]+)"', (ICON_DIR / f"{ICON_FILE.get(name, name)}.svg").read_text()).group(1)
    return (f'<path transform="translate({cx - size / 2:.2f} {cy - size / 2:.2f}) scale({size / 24:.4f})" '
            f'd="{d}" fill="{T["amber"]}"/>')


def build_stack():
    """One row of icon-only tiles, grouped: languages, ai & ml, serving and data."""
    body, x = "", 0
    for k, group in enumerate(STACK):
        x += GROUP_GAP * (k > 0)
        for name in group:
            body += (f'<rect x="{x + .5}" y=".5" width="{TILE - 1}" height="{TILE - 1}" rx="6" '
                     f'fill="{T["window"]}" stroke="{T["border"]}"/>' + icon(name, x + TILE / 2, TILE / 2))
            x += TILE + TILE_GAP
    names = [n for group in STACK for n in group]
    # no backdrop: the tiles carry their own fill, and a black band would show in the group gaps
    svg("stack.svg", x - TILE_GAP, TILE, body, "Stack: " + ", ".join(names), bg=None)


MARQUEE = [  # MARQUEE in the site's data/site.ts
    "Hi, I'm Davi Alcanfôr, a Brazilian AI engineer based in São Paulo.", "building AI @ PicPay",
    "studying at Instituto J&F", "python · rust", "portuguese, spanish and french", "I write on Medium",
]


def build_marquee():
    h, size, gap = 40, 13, 32
    x, items = 0.0, ""
    for item in MARQUEE:
        items += text(item, MONO, size, round(x, 2), 25, T["amber"])
        x += len(item) * cw(size) + gap
        # diamond separator in --fg-dim, like the site's <i>◆</i>
        items += f'<rect x="{x - gap / 2 - 3:.2f}" y="17" width="5" height="5" fill="{T["amber_dim"]}" ' \
                 f'transform="rotate(45 {x - gap / 2 - 0.5:.2f} 19.5)"/>'
    cycle = x
    css = (f"@keyframes m{{to{{transform:translateX(-{cycle:.2f}px)}}}}"
           f".m{{animation:m {cycle / 30:.1f}s linear infinite}}"
           "@media (prefers-reduced-motion:reduce){.m{animation:none}}")
    body = f'<g class="m">{items}<g transform="translate({cycle:.2f} 0)">{items}</g></g>'
    svg("marquee.svg", PAGE_W, h, body, " · ".join(MARQUEE), css)


LINK_ICONS = {  # Lucide paths from the site's icons.ts (24x24, stroke); "site" is the >_ favicon
    "site": '<path d="M5 7l5 5-5 5"/><path d="M13 17h7"/>',
    "linkedin": '<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/>'
                '<rect width="4" height="12" x="2" y="9"/><circle cx="4" cy="4" r="2"/>',
    "mail": '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
}
LINKS = [("site", "alcanfor.vercel.app"), ("linkedin", "linkedin"), ("medium", "medium"), ("mail", "email")]


def build_links():
    h, size = 40, 13
    for key, label in LINKS:
        w = round(16 + 18 + 10 + len(label) * cw(size) + 16)
        body = f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="6" fill="{T["window"]}" stroke="{T["border"]}"/>'
        if key == "medium":  # the site draws Medium's icon as the letters "Me"
            body += text("Me", MONO_BOLD, 12, 25, 25, T["amber"], "middle", -1.5)
        else:
            body += (f'<g transform="translate(16 11) scale(.75)" fill="none" stroke="{T["amber"]}" stroke-width="2" '
                     f'stroke-linecap="round" stroke-linejoin="round">{LINK_ICONS[key]}</g>')
        body += text(label, MONO, size, 44, 25, T["amber"])
        svg(f"link-{key}.svg", w, h, body, label, bg="black")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    build_marquee()
    build_links()
    build_stack()
    build_cover()
    for p in sorted(OUT.iterdir()):
        print(f"{p.name:28} {p.stat().st_size / 1024:8.1f} KB")


if __name__ == "__main__":
    main()
