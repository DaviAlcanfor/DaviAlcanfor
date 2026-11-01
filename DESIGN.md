---
name: Davi Alcanfôr GitHub Profile (terminal)
description: A short, amber-on-black profile in the style of alcanfor.vercel.app.
colors:
  black: "#000000"
  window: "#0B0B0B"
  bar: "#151515"
  border: "#2A2A2A"
  muted: "#666666"
  dim: "#A39D90"
  amber_dim: "#8C6415"
  amber: "#FFB627"
  amber_hi: "#FFD27A"
typography:
  label: { fontFamily: "Martian Mono 400 (OFL), as paths", fontSize: "13px" }
components:
  marquee: { file: "assets/terminal/marquee.svg", height: "40px", width: "100%" }
  cover:   { file: "assets/terminal/cover.gif", size: "840x300", width: "100%" }
  link:    { file: "assets/terminal/link-*.svg", height: "40px" }
  stack:   { file: "assets/terminal/stack.svg", height: "40px", tile: "40x40", icon: "20px" }
---

# Design system: terminal

`README.md` is the profile. `README.darksouls.md` and `DESIGN.darksouls.md` hold the gothic
version, kept in reserve. This one follows [alcanfor.vercel.app](https://alcanfor.vercel.app)
(source: `DaviAlcanfor/portfolio`), so the profile and the site read as one thing.

## Layout

Four things up front, and everything else folded away:

1. **Marquee:** the site's top line.
2. **Cover:** the centerpiece.
3. **Links:** website, LinkedIn, Medium and email.
4. **Stack:** one compact row of icons.

Below them, a `<details>` block (`$ cat ~/about.md`) holds the long version in native Markdown:
about, projects, the full stack and off hours. It costs nothing while it is closed, and it reads
well on phones.

## Method

- `python build_terminal.py` regenerates everything in `assets/terminal/`, deterministically.
  It reuses the path-text primitives from `build_assets.py` (the dark-souls builder).
- Tokens are copied from the site: `--fg`, `--fg-hi` and `--fg-dim` in `global.css`, and the
  greys of the projects terminal in `Terminal.astro`.
- Content is copied from `src/data/site.ts`: roles, bio and marquee. The project lines in the
  README's `<details>` come from its `PROJECTS`. When the site changes, update both.
- No photo. The cover is drawn entirely in code.

## Components

- **Marquee.** The items from `MARQUEE`, separated by `amber_dim` diamonds, scrolling at 30 px/s
  in a seamless CSS loop.
- **Cover.** A 90-frame GIF at 10 fps (9 s, 322 KB):
  - still grey glyph columns, with falling amber streams over them
  - the name decodes once per loop
  - the role cycles through `SITE.roles` every 3 s, with the site's scramble (unresolved
    letters are random glyphs in `amber_dim`) and a few torn slices at each change
  - the bio sits in the bottom-right corner, as on the site
- **Link.** A `window` box with a `border` outline and 6 px radius, a Lucide icon from the
  site's `icons.ts` (or the `>_` favicon for the website), and a lowercase label.
- **Stack.** Icon-only 40 px tiles in the same style as the links, so the two rows read as one
  block.
  - Three groups, 16 px apart: Python, Rust, Go | LangGraph, PyTorch | FastAPI, Postgres,
    Docker. Tiles within a group sit 6 px apart.
  - Marks: Simple Icons 16.36.0 (CC0), vendored in `tools/icons/`, filled in amber.
  - Only what defines the work goes here. The full list lives in the `<details>` block.

## Rules

1. **Amber is for names, links and marks.** No glow: the site keeps glow for hover only.
2. **Keep the surface short.** New material goes in the `<details>` block, as Markdown, not as
   another image.
3. **Motion:** only the cover and the marquee move. `prefers-reduced-motion` stops the marquee.
4. **Accessibility.** Each SVG carries `<title>` and `role="img"`. The cover's alt text
   describes its animation.

## Previews

Render the SVGs and look at them:

```bash
python -c "import resvg_py, pathlib; [pathlib.Path(f'previews/{p.stem}.png').write_bytes(bytes(resvg_py.svg_to_bytes(svg_path=str(p)))) for p in pathlib.Path('assets/terminal').glob('*.svg')]"
```
