---
name: Davi Alcanfôr GitHub Profile
description: A penitent's chapel. Gothic, candlelit, restrained. Pixel art on a void ground.
colors:
  void: "#0E0B0A"
  shadow: "#1A1412"
  cloak: "#241A18"
  cloak_lit: "#3A2A26"
  stone_dark: "#2A2220"
  stone: "#3B312D"
  stone_lit: "#5A4A40"
  steel: "#4E5B57"
  parchment: "#8C7F68"
  bone: "#D8CBB0"
  blood: "#6E1414"
  crimson: "#A3241C"
  gold: "#B08A3E"
  gold_light: "#E0B860"
  flame: "#F4E2B0"
typography:
  display: { fontFamily: "Cinzel 700 (OFL), as paths", fontSize: "46px" }
  heading: { fontFamily: "Cinzel 700 (OFL), as paths", fontSize: "22-26px" }
  epitaph: { fontFamily: "Cinzel 400 (OFL), as paths", fontSize: "15-22px" }
  label:   { fontFamily: "Silkscreen (OFL), as paths", fontSize: "16px" }
components:
  cover:    { file: "assets/cover.gif", size: "960x320 (240x80 at 4x)", width: "100%" }
  intro:    { file: "assets/intro.svg", size: "640x176" }
  link:     { file: "assets/link-*.svg", height: "52px" }
  header:   { file: "assets/header-*.svg", size: "560x52", width: "560px" }
  relic:    { file: "assets/relic-*.svg", height: "36px" }
  item:     { file: "assets/item-*.svg", height: "64px" }
  votive:   { file: "assets/votive-*.svg", size: "260x220", width: "250px" }
  divider:  { file: "assets/divider-{candle,thorn}.svg", size: "840x48", width: "100%" }
  footer:   { file: "assets/footer.svg", size: "640x200", width: "100%" }
---

# Design system

Blasphemous is the visual base, Sekiro sets the restraint and Dark Souls sets the tone. The page is
serious: no memes and no exclamation marks. Everything here is original. No characters, logos or
art from those games (or from Valorant, Rainbow Six Siege or GeoGuessr) appear anywhere.

## Method

- **One painted asset.** `assets/cover.gif` is the only image that starts from an illustration.
  Everything else is generated.
- **`build_assets.py` regenerates everything** deterministically: `python build_assets.py`.
- **Pixel art is data.** Sprites are lists of strings. Each character maps to a palette token, and
  each horizontal run becomes one `<rect>` inside `<g shape-rendering="crispEdges">`.
- **Text is geometry.** GitHub serves SVGs through `<img>`, which blocks external fonts, so fontTools
  draws every glyph into a single `<path>`. The fonts live in `tools/fonts/` with their OFL licenses.
- **Preview before committing.** `python tools/preview.py` renders every SVG with resvg and tiles
  them into contact sheets in `tools/out/preview/`. Check those sheets for clipped text,
  misalignment and contrast.

## Tokens

`PALETTE` in `tools/cover_procedural.py` is the only source of color. `build_assets.py` imports it
as `C`. No hex value may appear anywhere else.

| Role | Tokens |
| --- | --- |
| Ground | `void` (every SVG background), `shadow`, `stone_dark` |
| Stone and frames | `stone`, `stone_lit` |
| Ink | `bone` (primary text), `parchment` (secondary text) |
| Accent (wounds) | `blood`, `crimson`, used sparingly for rules, drops and the language relics |
| Accent (light) | `gold`, `gold_light`, `flame`, used only for candles, frames and the AI relics |

## Rules

1. **Own your dark ground.** Every SVG paints a full `void` rect first, so the page reads the same
   on GitHub's light and dark themes.
2. **Stepped corners only.** Boxes come from `stepped()`, which cuts corners in square steps. Never
   use `rx`.
3. **Motifs:** candle, crown of thorns, retable frame, wax drop. Nothing else.
4. **Animation is CSS only, and rare.** The only animated SVG flame is in the candle divider and the
   footer: a three-frame `step-end` loop. `prefers-reduced-motion` freezes it on frame 0.
5. **Accessibility.** Each SVG carries `<title>` and `role="img"` when it means something.
   Decorative SVGs get `aria-hidden` and an empty `alt=""` in the README.
6. **Width.** Nothing is wider than 840 px. The intro and footer are 640 px and section headers
   560 px, so their text stays legible when phones scale them down. Votives wrap from three across to one per row.
7. **Native text for prose.** The About paragraph, item descriptions and stack lines are Markdown,
   so they stay searchable, selectable and readable by screen readers.

## Components

- **Cover.** `source/cover_thumb.jpg` goes through: crop 3:1, LANCZOS resize to 240x80, gamma 0.72,
  contrast 1.45, Bayer 4x4 dither at strength 14 into the palette, then a 4x nearest-neighbor
  upscale. 24 frames of 110 ms. Candle glow shifts brightness by ±12% around its mean, and flames
  and embers are drawn at `FLAME_TIPS`. If `source/cover_source.png` exists, the script uses it
  instead of the thumbnail.
- **Intro.** A double retable frame (gold, then `stone_dark`). The crown of thorns breaks the top
  rail. The name is in Cinzel 700 at 46 px, the role in Cinzel 400 at 17 px, with an unlit candle
  on each side.
- **Link plaque.** A stone slab with a lit top edge, a 10x10 pixel icon and a Silkscreen label.
- **Section header.** A crimson drop, the Cinzel title, then a bar of 6x4 blocks that fades
  crimson → blood → stone_dark, all over a 1 px `stone` rule.
- **Relic.** A stepped badge, colored by group:
  - languages: `crimson` / `blood` with `bone` ink
  - AI and ML: `gold_light` / `gold` with `void` ink
  - infrastructure: `stone_lit` / `stone` with `bone` ink

  Python, Rust and Go get simplified pixel marks. The rest get a wax drop.
- **Item card.** A 16x16 icon in a framed cell, the project name in Cinzel at 26 px, and a `blood`
  underline with a short `gold` segment. The description below is written as an item description:
  two or three sober sentences, true to the repo's README.
- **Votive.** An arched tablet built from five narrowing steps, with a Roman numeral, a 15x15
  generic icon at 3x, the name, a blood rule, a wax drop and a ledge.
- **Divider.** Twin stone rules with gold drops at both ends and either a candle (animated) or a
  crown of thorns in the center.
- **Footer.** The epitaph in Cinzel 400, with three candles on a slab.

## External cards

All three are built by `.github/workflows/activity.yml` (daily, on push to main, or by hand) and
published to the `output` branch. The README embeds them from `raw.githubusercontent.com`.

- **Stats and top-langs:** rendered by `stats-organization/github-readme-stats-action`, because the
  public github-readme-stats instance answers 503. They are recolored through `CARD_COLORS`
  (`bg_color=0E0B0A`, `title_color=D8CBB0`, `text_color=8C7F68`, `icon_color=A3241C`,
  `ring_color=B08A3E`). Language colors stay GitHub's own, which is the one sanctioned exception to
  the palette.
- **Contribution snake:** generated by Platane/snk with palette colors. Its background is
  transparent, because snk offers no fill option.
