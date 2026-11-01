"""Turn an AI-generated illustration into palette-locked pixel art.

Usage: python pixelize.py input.png [--width 240]
Writes out/<name>_pixel.png (upscaled 4x) using the cover's palette.
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance

from cover_procedural import BAYER4, PAL_RGB, SCALE, to_image

OUT = Path(__file__).parent / "out"


def crop_to_ratio(img, ratio):
    w, h = img.size
    target_h = int(w / ratio)
    if target_h <= h:
        top = (h - target_h) // 2
        return img.crop((0, top, w, top + target_h))
    target_w = int(h * ratio)
    left = (w - target_w) // 2
    return img.crop((left, 0, left + target_w, h))


def quantize_dithered(rgb, strength):
    h, w, _ = rgb.shape
    noise = np.tile(BAYER4, (h // 4 + 1, w // 4 + 1))[:h, :w][..., None] * strength
    flat = (rgb + noise).reshape(-1, 1, 3)
    return ((flat - PAL_RGB[None]) ** 2).sum(-1).argmin(1).reshape(h, w)


def pixelize(path, width, ratio=3.0, contrast=1.25, dither=24):
    img = Image.open(path).convert("RGB")
    img = crop_to_ratio(img, ratio)
    img = ImageEnhance.Contrast(img).enhance(contrast)
    small = img.resize((width, int(width / ratio)), Image.LANCZOS)
    idx = quantize_dithered(np.asarray(small, dtype=float), dither)
    return to_image(idx)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image")
    parser.add_argument("--width", type=int, default=240)
    args = parser.parse_args()
    out = OUT / f"{Path(args.image).stem}_pixel.png"
    pixelize(args.image, args.width).save(out)
    print(out, f"(scale {SCALE}x)")


if __name__ == "__main__":
    main()
