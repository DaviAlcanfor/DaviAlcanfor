---
name: Davi Alcanfôr GitHub Profile (terminal)
description: The profile as a terminal session, in the style of alcanfor.vercel.app.
colors:
  black: "#000000"
  window: "#0B0B0B"
  bar: "#151515"
  rule: "#222222"
  border: "#2A2A2A"
  dot: "#2C2C2C"
  faint: "#555555"
  muted: "#666666"
  label: "#777777"
  dim: "#A39D90"
  ink: "#D8D2C4"
  amber_low: "#4D370C"
  amber_dim: "#8C6415"
  amber: "#FFB627"
  amber_hi: "#FFD27A"
typography:
  body: { fontFamily: "Martian Mono 400 (OFL), as paths", fontSize: "14px", lineHeight: "26px" }
  heading: { fontFamily: "Martian Mono 600 (OFL), as paths", fontSize: "18px" }
  chrome: { fontFamily: "Martian Mono 400 (OFL), as paths", fontSize: "11-13px" }
components:
  marquee:  { file: "assets/terminal/marquee.svg", size: "840x40", width: "100%" }
  cover:    { file: "assets/terminal/cover.gif", size: "840x300", width: "100%" }
  link:     { file: "assets/terminal/link-*.svg", height: "40px" }
  window:   { file: "assets/terminal/{whoami,stack,projects,offhours,footer}.svg", width: "720px" }
  project:  { file: "assets/terminal/project-*.svg", size: "480x40" }
  prompt:   { file: "assets/terminal/prompt-activity.svg", size: "720x36" }
---

# Design system: terminal

`README.md` is the profile; `README.darksouls.md` and `DESIGN.darksouls.md` are the gothic
version, kept in reserve. This one follows [alcanfor.vercel.app](https://alcanfor.vercel.app)
(source: `DaviAlcanfor/portfolio`), so the profile and the site read as one thing.

## Method

- `python build_terminal.py` regenerates everything in `assets/terminal/`, deterministically.
  It reuses the path-text primitives from `build_assets.py` (the dark-souls builder).
- Tokens are copied from the site: `--fg`, `--fg-hi` and `--fg-dim` in `global.css`, and the
  greys of the projects terminal in `Terminal.astro`. `amber_low` is the only new one: amber at
  30% over black, derived the same way as `--fg-dim`, for the lowest contribution level.
- Content is copied from `src/data/site.ts`: roles, bio, marquee, playlist and project
  descriptions. When the site changes, update the lists at the top of each builder.
- No photo. The cover is drawn entirely in code.

## Metaphor

The README is one terminal session. Every section is a command at the `davi@github:~$` prompt:
`whoami`, `cat stack.toml`, `ls projects/` with `cat projects/*/README`, `ls ~/off-hours/`,
`now-playing --shuffle`, `git log --graph`, and finally `exit`.

## Components

- **Marquee.** The site's top line: the items from `MARQUEE`, separated by `amber_dim`
  diamonds, scrolling at 30 px/s in a seamless CSS loop.
- **Cover.** A 90-frame GIF at 10 fps (9 s, 322 KB):
  - still grey glyph columns, with falling amber streams over them
  - the name decodes once per loop
  - the role cycles through `SITE.roles` every 3 s, with the site's scramble (unresolved
    letters are random glyphs in `amber_dim`) and a few torn slices at each change
  - the bio sits in the bottom-right corner, as on the site
- **Link.** A `window` box with a `border` outline and 6 px radius, a Lucide icon from the
  site's `icons.ts` (or the `>_` favicon for the website), and a lowercase label.
- **Window.** The site's projects terminal: `bar` title strip with three `dot` circles, the
  title in `label`, `esc` in `faint`, and a body in `window` with an 8 px radius.
  - Commands type in once on load, as a window-colored cover slides off one character per step.
  - Output lines fade in 70 ms apart.
  - A blinking amber block caret waits at the end.
- **Project heading.** `── name ─────`, as the site's `h2::after` draws it. Below it, the
  README carries native text: the description, then `stack` and `repo` (and `demo`).
- **Now playing.** Four equalizer bars and the site's playlist, one track every 3 s.

## Rules

1. **Amber is for prompts, names and links. `ink` is for what you type, `dim` for what the
   machine prints.** No glow inside windows: the site keeps glow for hover only.
2. **Animations run once, except** the caret, marquee, equalizer and playlist, which loop.
3. **The static state is the final state.** Every animation only hides things while it plays:
   the typing cover rests past the command, faded lines end fully visible, and the first track
   is shown by default. Renderers that skip CSS animation (resvg, some apps) still show the
   whole session. `prefers-reduced-motion` turns the motion off.
4. **Width.** Windows are 720 px with 63 characters per line at most. They shrink to about 7 px
   text on phones, so every window has an alt text that repeats its content. Project
   descriptions are native Markdown.
5. **Accessibility.** Each SVG carries `<title>` and `role="img"`. Animated text is also in
   the alt text.

## External cards

`.github/workflows/activity.yml` publishes `stats-terminal.svg`, `top-langs-terminal.svg` and
`snake-terminal.svg` to the `output` branch with these tokens. It publishes the dark-souls
cards beside them, so `README.darksouls.md` keeps working.

## Previews

Render the SVGs (they show their final state) and look at them:

```bash
python -c "import resvg_py, pathlib; [pathlib.Path(f'previews/{p.stem}.png').write_bytes(bytes(resvg_py.svg_to_bytes(svg_path=str(p)))) for p in pathlib.Path('assets/terminal').glob('*.svg')]"
```

To check the animations, open the README in a real browser.
