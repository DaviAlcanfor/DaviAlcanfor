"""Regenerate every README asset: the animated cover and all SVG components.

Colors come from PALETTE in tools/cover_procedural.py (the single source of
truth). Text is converted to paths with fontTools because GitHub renders SVGs
through <img>, which blocks external fonts. Pixel art is drawn from string
grids into crisp <rect> runs. Output is deterministic.

    python tools/build_assets.py
"""
import sys
from html import escape
from pathlib import Path

import numpy as np
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image, ImageEnhance

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from cover_procedural import (  # noqa: E402
    FRAME_MS, FRAMES, H, PALETTE as C, W, draw_embers, draw_flames, ember_particles, light_map, to_image,
)
from pixelize import crop_to_ratio, quantize_dithered  # noqa: E402

OUT = ROOT / "readmes" / "darksouls" / "assets"
SOURCE = ROOT / "source"
FONTS = ROOT / "tools" / "fonts"

# Cover look, matched against source/cover_reference.png.
GAMMA, CONTRAST, DITHER = 0.72, 1.45, 14
GLOW = 0.12  # brightness swing of the candle glow, kept subtle on purpose
# Flame tips in the 240x80 cover: tall candle, floor candle, tongues on the altar.
FLAME_TIPS = [(222, 7), (122, 60), (131, 43), (139, 35), (151, 27), (190, 27), (201, 16), (213, 29)]

SERIF = instantiateVariableFont(TTFont(FONTS / "Cinzel.ttf"), {"wght": 700})
SERIF_LIGHT = instantiateVariableFont(TTFont(FONTS / "Cinzel.ttf"), {"wght": 400})
PIXEL = TTFont(FONTS / "Silkscreen.ttf")


# ── cover ────────────────────────────────────────────────────────────────

def build_cover():
    src = SOURCE / "cover_source.png"
    if not src.exists():
        src = SOURCE / "cover_thumb.jpg"  # the thumbnail the approved look was made from
    img = crop_to_ratio(Image.open(src).convert("RGB"), 3.0).resize((W, H), Image.LANCZOS)
    lifted = ((np.asarray(img, float) / 255) ** GAMMA * 255).round().astype("uint8")
    base = np.asarray(ImageEnhance.Contrast(Image.fromarray(lifted)).enhance(CONTRAST), float)

    lights = [light_map(f, FLAME_TIPS) for f in range(FRAMES)]
    mean_light = sum(lights) / FRAMES
    particles = ember_particles(seed=3, count=22, tops=FLAME_TIPS)
    frames = []
    for f in range(FRAMES):
        rgb = base * (1 + GLOW * (lights[f] - mean_light)[..., None] / 0.2)
        idx = quantize_dithered(np.clip(rgb, 0, 255), DITHER)
        draw_flames(idx, f, FLAME_TIPS)
        draw_embers(idx, f, particles)
        frames.append(to_image(idx))
    frames[0].save(OUT / "cover.gif", save_all=True, append_images=frames[1:],
                   duration=FRAME_MS, loop=0, disposal=1)


# ── svg primitives ───────────────────────────────────────────────────────

def rect(x, y, w, h, fill, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{extra}/>'


def stepped(x, y, w, h, fill, step=2, n=2):
    """A box whose corners are cut in n square steps, never rounded."""
    return "".join(rect(x + i * step, y + (n - i) * step, w - 2 * i * step, h - 2 * (n - i) * step, fill)
                   for i in range(n + 1))


def sprite(rows, pal, x, y, u, extra=""):
    """Pixel grid of chars -> horizontal <rect> runs. '.' or unknown chars are transparent."""
    assert len({len(r) for r in rows}) == 1, rows
    out = []
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            ch, start = row[c], c
            while c < len(row) and row[c] == ch:
                c += 1
            if ch in pal:
                out.append(rect(x + start * u, y + r * u, (c - start) * u, u, pal[ch]))
    return f'<g shape-rendering="crispEdges"{extra}>{"".join(out)}</g>'


def _glyphs(value, font):
    cmap = font.getBestCmap()
    return [cmap[ord(ch)] for ch in value]


def text_width(value, font, size, tracking=0):
    gs, names = font.getGlyphSet(), _glyphs(value, font)
    return sum(gs[n].width for n in names) * size / font["head"].unitsPerEm + tracking * (len(names) - 1)


def text(value, font, size, x, y, fill, anchor="start", tracking=0):
    """Text as a single <path>; y is the baseline."""
    gs, s = font.getGlyphSet(), size / font["head"].unitsPerEm
    x -= {"start": 0, "middle": 0.5, "end": 1}[anchor] * text_width(value, font, size, tracking)
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
    for name in _glyphs(value, font):
        gs[name].draw(TransformPen(pen, (s, 0, 0, -s, x, y)))
        x += gs[name].width * s + tracking
    return f'<path d="{pen.getCommands()}" fill="{fill}"/>'


def svg(name, w, h, body, title, style=""):
    alt = f'<title>{escape(title)}</title>' if title else ""
    role = f'role="img" aria-label="{escape(title)}"' if title else 'aria-hidden="true"'
    css = f"<style>{style}</style>" if style else ""
    (OUT / name).write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" {role}>'
        f'{alt}{css}{rect(0, 0, w, h, C["void"])}{body}</svg>\n', encoding="utf-8")


# ── pixel motifs ─────────────────────────────────────────────────────────

FLAME_FRAMES = [
    [".g...", ".lg..", "glfg.", ".lfl.", ".lfl.", "..l.."],
    ["..g..", "..l..", ".glg.", ".lfl.", ".lfl.", "..l.."],
    ["...g.", "..gl.", ".gflg", ".lfl.", ".lfl.", "..l.."],
]
FLAME_PAL = {"g": C["gold"], "l": C["gold_light"], "f": C["flame"]}
CANDLE = [
    "..k..",
    ".bbb.",
    ".bbp.",
    "pbbb.",
    "pbbb.",
    ".bbb.",
    ".bbp.",
    ".bbb.",
    ".bbb.",
    "ggggg",
]
CANDLE_PAL = {"k": C["shadow"], "b": C["bone"], "p": C["parchment"], "g": C["gold"]}
THORNS = [
    "..t...t.....t...t..",
    "...t.bbbbbbbbb.t...",
    ".tbbbb.......bbbbt.",
    "bbt.............tbb",
    "bb...............bb",
    "tbb.............bbt",
    ".bbbbt.......tbbbb.",
    "...bbbbbbbbbbbbb...",
    "..t...t..d..t...t..",
    ".........d.........",
]
THORN_PAL = {"b": C["stone_lit"], "t": C["parchment"], "d": C["crimson"]}
DROP = [".w.", "www", "www", ".w."]

FLICKER_CSS = (
    "@keyframes k{0%{opacity:1}33.3%{opacity:0}100%{opacity:0}}"
    ".f{opacity:0;animation:k .9s step-end infinite}.f0{opacity:1}"
    ".f1{animation-delay:-.3s}.f2{animation-delay:-.6s}"
    "@media (prefers-reduced-motion:reduce){.f{animation:none}}"
)


def candle(x, y, u=2, animated=True):
    """Candle with a 3-frame CSS flame; (x, y) is the top-left of the flame box."""
    if animated:
        flame = "".join(sprite(fr, FLAME_PAL, x, y, u, f' class="f f{i}"') for i, fr in enumerate(FLAME_FRAMES))
    else:
        flame = sprite(FLAME_FRAMES[1], FLAME_PAL, x, y, u)
    return flame + sprite(CANDLE, CANDLE_PAL, x, y + 6 * u, u)


# ── components ───────────────────────────────────────────────────────────

def build_dividers():
    w, h, cx = 840, 48, 420
    rule = lambda x0, x1: rect(x0, 25, x1 - x0, 1, C["stone"]) + rect(x0, 26, x1 - x0, 1, C["shadow"])
    ends = sprite(DROP, {"w": C["gold"]}, 52, 22, 2) + sprite(DROP, {"w": C["gold"]}, 782, 22, 2)
    lines = rule(64, cx - 30) + rule(cx + 30, 776) + ends
    svg("divider-candle.svg", w, h, lines + candle(cx - 5, 4), "", FLICKER_CSS)
    svg("divider-thorn.svg", w, h, lines + sprite(THORNS, THORN_PAL, cx - 19, 14, 2), "")


def build_intro():
    w, h, cx = 640, 176, 320  # narrower than the page so text stays legible when scaled on phones
    frame = stepped(20, 8, 600, 160, C["gold"], 4) + stepped(22, 10, 596, 156, C["void"], 4)
    frame += stepped(28, 16, 584, 144, C["stone_dark"], 4) + stepped(30, 18, 580, 140, C["void"], 4)
    # the crown of thorns breaks the top rail
    frame += rect(cx - 28, 0, 56, 24, C["void"])
    body = frame + sprite(THORNS, THORN_PAL, cx - 19, 1, 2)
    body += text("DAVI ALCANFÔR", SERIF, 46, cx, 92, C["bone"], "middle", 3)
    body += rect(cx - 120, 108, 240, 1, C["blood"]) + sprite(DROP, {"w": C["crimson"]}, cx - 3, 104, 2)
    body += text("AI ENGINEER · SÃO PAULO, BRAZIL", SERIF_LIGHT, 17, cx, 142, C["parchment"], "middle", 2)
    body += candle(46, 70, 3, False) + candle(w - 46 - 15, 70, 3, False)
    svg("intro.svg", w, h, body, "Davi Alcanfôr. AI Engineer, São Paulo, Brazil.")


ICONS = {
    "site": (["...bbbb...", "..bcrrcb..", ".bcrrrrcb.", ".bcrrrrcb.", ".bbbbbbbb.",
              ".bcrbbrcb.", ".bcrbbrcb.", ".bcrbbrcb.", ".bbbbbbbb.", "bbbbbbbbbb"],
             {"b": C["stone_lit"], "c": C["crimson"], "r": C["blood"]}),
    "linkedin": (["wwwwwwwwww", "ww.....pww", "w.w...p.ww", "w..w.p..ww", "w...ccc..w",
                  "w..ccccc.w", "w...ccc..w", "w.........", "wwwwwwwwww", ".........."],
                 {"w": C["bone"], "p": C["parchment"], "c": C["crimson"]}),
    "medium": ([".........w", "........ww", ".......wwp", "......wwp.", ".....wwp..",
                "....wwp...", "...wwp....", "...wp.....", "..g.......", ".g........"],
               {"w": C["bone"], "p": C["parchment"], "g": C["gold_light"]}),
}


def build_links():
    for key, label in (("site", "WEBSITE"), ("linkedin", "LINKEDIN"), ("medium", "MEDIUM")):
        tw = text_width(label, PIXEL, 16, 1)
        w, h = round(76 + tw), 52
        rows, pal = ICONS[key]
        body = stepped(4, 4, w - 8, h - 8, C["stone_lit"], 2) + stepped(4, 6, w - 8, h - 10, C["stone"], 2)
        body += rect(10, h - 8, w - 20, 2, C["stone_dark"])
        body += sprite(rows, pal, 22, 16, 2) + text(label, PIXEL, 16, 54, 33, C["bone"], tracking=1)
        svg(f"link-{key}.svg", w, h, body, label.title())


LANG_ICONS = {
    "Python": (["...ggggg....", "...g.ggg....", "...ggggg....", "......gg....", "ggggggggg.ww",
                "gggggggg.www", "ggg.wwwwwwww", "gg.wwwwwwwww", "....ww......", "....wwwww...",
                "....www.w...", "....wwwww..."], {"g": C["gold_light"], "w": C["bone"]}),
    "Rust": (["....w..w....", "..wwwwwwww..", ".wwrrrrrrww.", "wwrwwwwwrrww", ".wrwwrrwwrw.",
              ".wrwwwwwrrw.", "wwrwwwwrrrww", ".wrwwrwwrrw.", ".wrwwrrwwrw.", "wwrrrrrrrrww",
              "..wwwwwwww..", "....w..w...."], {"w": C["bone"], "r": C["blood"]}),
    "Go": (["............", "....wwwwwwww", "............", "wwwwwwwwww..", "............",
            "......wwwwww", "............"], {"w": C["bone"]}),
}
STACK = [
    ("lang", ["Python", "Rust", "Go"]),
    ("ai", ["LangGraph", "LangChain", "Prophet", "LightGBM"]),
    ("infra", ["FastAPI", "Postgres", "Redis", "Qdrant", "Docker"]),
]
BADGE_TONES = {
    "lang": (C["crimson"], C["blood"], C["bone"]),
    "ai": (C["gold_light"], C["gold"], C["void"]),
    "infra": (C["stone_lit"], C["stone"], C["bone"]),
}


def badge_name(label):
    return f"relic-{label.lower()}.svg"


def build_badges():
    for group, labels in STACK:
        top, fill, ink = BADGE_TONES[group]
        for label in labels:
            caps = label.upper()
            icon_w = 24 + 8 if label in LANG_ICONS else 6 + 8
            w, h = round(12 + icon_w + text_width(caps, PIXEL, 16, 1) + 12), 36
            body = stepped(2, 2, w - 4, h - 4, top, 2) + stepped(2, 4, w - 4, h - 6, fill, 2)
            if label in LANG_ICONS:
                rows, pal = LANG_ICONS[label]
                body += sprite(rows, pal, 12, (h - len(rows) * 2) // 2 + 1, 2)
            else:
                body += sprite(DROP, {"w": ink}, 12, 14, 2)
            body += text(caps, PIXEL, 16, 12 + icon_w, 24, ink, tracking=1)
            svg(badge_name(label), w, h, body, label)


ITEM_ICONS = {
    "nb2ob": (["................", ".bbbbbb..bbbbbb.", "bppppppbbppppppb", "bpkkkkpbbpkkkkpb",
               "bppppppbbppppppb", "bpkkkppbbpkkkkpb", "bppppppbbppppppb", "bpkkkkpbbpkkppb.",
               "bppppppbbppppppb", "bpkkpppbbpkkkkpb", "bppppppbbppppppb", "bbbbbbbbbbbbbbbb",
               ".......cc.......", ".......cc.......", ".......c........", "................"],
              {"b": C["parchment"], "p": C["bone"], "k": C["stone"], "c": C["crimson"]}),
    "assessor-ai": (["........g.......", ".......ggg......", "gggggggggggggggg", ".g.....g.....g..",
                     ".g.....g.....g..", "g.g....g....g.g.", "g.g....g....g.g.", "g..g...g...g..g.",
                     "yyyyy..g..yyyyy.", ".yyy...g...yyy..", ".......g........", ".......g........",
                     ".......g........", ".....ggggg......", "....ggggggg.....", "................"],
                    {"g": C["gold"], "y": C["gold_light"]}),
    "hybridts": (["gggggggggggggg..", ".ssssssssssss...", "..bffffffffb....", "...bffffffb.....",
                  "....bffffb......", ".....bffb.......", "......bb........", "......bb........",
                  ".....b.fb.......", "....b..f.b......", "...b...f..b.....", "..b..ffff..b....",
                  ".bffffffffffb...", ".ssssssssssss...", "gggggggggggggg..", "................"],
                 {"g": C["gold"], "s": C["stone_lit"], "b": C["parchment"], "f": C["crimson"]}),
    "anubis": (["................", "....gggg........", "...gg..gg.......", "..gg....gg......",
                "..g......g......", "..gg....gg......", "...gg..gg.......", "....gggg........",
                ".....gg.........", ".....gg.........", ".....gggg.......", ".....gg.........",
                ".....ggg........", ".....gg.........", ".....gggg.......", "................"],
               {"g": C["gold"]}),
    "frigus-ai": (["...............", ".......w.......", ".....w.w.w.....", "......www......",
                   ".w.....w.....w.", "..w..s.w.s..w..", "...ww.sws.ww...", "wwwwwwwwwwwwwww",
                   "...ww.sws.ww...", "..w..s.w.s..w..", ".w.....w.....w.", "......www......",
                   ".....w.w.w.....", ".......w.......", "...............", "..............."],
                  {"w": C["bone"], "s": C["steel"]}),
}
PROJECTS = ["nb2ob", "assessor-ai", "hybridts", "anubis", "frigus-ai"]


def build_project_cards():
    for name in PROJECTS:
        rows, pal = ITEM_ICONS[name]
        tw = text_width(name.upper(), SERIF, 26, 2)
        w, h = round(86 + tw + 24), 64
        body = stepped(4, 4, 56, 56, C["stone_dark"], 2) + stepped(6, 6, 52, 52, C["void"], 2)
        body += sprite(rows, pal, 16, 16, 2)
        body += text(name.upper(), SERIF, 26, 80, 40, C["bone"], tracking=2)
        body += rect(80, 50, round(tw), 1, C["blood"]) + rect(80, 52, round(tw * 0.35), 1, C["gold"])
        svg(f"item-{name}.svg", w, h, body, name)


VOTIVE_ICONS = {
    "geoguessr": ([".....rrrrr.....", "...rrrrrrrrr...", "..rrrrcccrrrr..", "..rrrc...crrr..",
                   "..rrrc...crrr..", "..rrrrcccrrrr..", "...rrrrrrrrr...", "....rrrrrrr....",
                   ".....rrrrr.....", "......rrr......", ".......r.......", ".......r.......",
                   "...sssssssss...", ".ss.........ss.", "...sssssssss..."],
                  {"r": C["crimson"], "c": C["bone"], "s": C["stone_lit"]}),
    "valorant": ([".......b.......", ".......b.......", ".......b.......", "...............",
                  ".......c.......", "...............", "bbb..c.c.c..bbb", "...............",
                  ".......c.......", "...............", ".......b.......", ".......b.......",
                  ".......b.......", "...............", "..............."],
                 {"b": C["bone"], "c": C["crimson"]}),
    "r6": (["ggggggggggggggg", "gsssssssssssssg", "gssssssbsssssg.", "gsssssbbbssssg.",
            "gssssssbsssssg.", "gsbbbbbbbbbbbg.", ".gssssbbbssssg.", ".gsssssbsssssg.",
            "..gssssbsssg...", "..gssssbsssg...", "...gsssbssg....", "....gssbsg.....",
            ".....ggggg.....", "......ggg......", ".......g......."],
           {"g": C["gold"], "s": C["blood"], "b": C["bone"]}),
}
VOTIVES = [("geoguessr", "GeoGuessr", "I"), ("valorant", "Valorant", "II"), ("r6", "Rainbow Six Siege", "III")]


def build_votives():
    w, h = 260, 220
    for key, label, numeral in VOTIVES:
        rows, pal = VOTIVE_ICONS[key]
        # arched tablet: stacked steps narrowing toward the top
        body = "".join(rect(30 + i * 14, 42 - i * 8, 200 - i * 28, 170, C["stone_dark"]) for i in range(5))
        body += "".join(rect(34 + i * 14, 46 - i * 8, 192 - i * 28, 162, C["shadow"]) for i in range(5))
        body += sprite(rows, pal, 130 - 22, 56, 3)
        body += text(numeral, SERIF_LIGHT, 13, 130, 30, C["gold"], "middle", 2)
        size = 20 if len(label) < 12 else 15
        body += text(label.upper(), SERIF, size, 130, 142, C["bone"], "middle", 1.5)
        body += rect(80, 156, 100, 1, C["blood"])
        body += sprite(DROP, {"w": C["crimson"]}, 127, 174, 2)
        body += rect(20, 206, 220, 6, C["stone"]) + rect(20, 206, 220, 1, C["stone_lit"])
        svg(f"votive-{key}.svg", w, h, body, f"Votive plaque: {label}")


def build_footer():
    w, h, cx = 640, 200, 320
    body = stepped(70, 164, 500, 20, C["stone_dark"], 4, 1) + rect(74, 164, 492, 1, C["stone_lit"])
    # candle height is 16 units, so y = ledge - 16u
    body += candle(cx - 48, 116, 3) + candle(cx - 10, 100, 4) + candle(cx + 33, 116, 3)
    body += text("EVERY FLAME BURNS LOWER.", SERIF_LIGHT, 22, cx, 50, C["bone"], "middle", 3)
    body += text("TEND IT ANYWAY.", SERIF_LIGHT, 22, cx, 82, C["parchment"], "middle", 3)
    svg("footer.svg", w, h, body, "Epitaph: Every flame burns lower. Tend it anyway.", FLICKER_CSS)


def main():
    OUT.mkdir(exist_ok=True)
    build_dividers()
    build_intro()
    build_links()
    build_badges()
    build_project_cards()
    build_votives()
    build_footer()
    build_cover()
    for p in sorted(OUT.iterdir()):
        print(f"{p.name:28} {p.stat().st_size / 1024:8.1f} KB")


if __name__ == "__main__":
    main()
