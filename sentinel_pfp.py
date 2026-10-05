"""sentinel_pfp.py - Generate a 512px avatar with gradient badge + letter emblem.

Purpose: dark-background profile picture with a gradient ring/badge and a
    single letter in the center (no personal names baked in).

Usage:
    python sentinel_pfp.py --letter S --out pfp.png --size 512
    python sentinel_pfp.py --letter X --theme ember --size 256 --out x.png

Platform: Windows + Linux. Requires Pillow (PIL).
    pip install Pillow
"""
import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("ERROR: Pillow is required. Install it with: pip install Pillow",
          file=sys.stderr)
    sys.exit(1)

BG = (10, 11, 14)
WHITE = (244, 245, 250)

# theme name -> (gradient_top, gradient_bottom)
THEMES = {
    "violet-cyan": ((124, 58, 237), (34, 211, 238)),
    "ember": ((239, 68, 68), (245, 158, 11)),
    "frost": ((14, 165, 233), (165, 243, 252)),
}

# Minimal 5x7 pixel font for the single letter/digit emblem.
FONT = {
    "A": [".XXX.", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"],
    "B": ["XXXX.", "X...X", "X...X", "XXXX.", "X...X", "X...X", "XXXX."],
    "C": [".XXXX", "X....", "X....", "X....", "X....", "X....", ".XXXX"],
    "D": ["XXXX.", "X...X", "X...X", "X...X", "X...X", "X...X", "XXXX."],
    "E": ["XXXXX", "X....", "X....", "XXXX.", "X....", "X....", "XXXXX"],
    "F": ["XXXXX", "X....", "X....", "XXXX.", "X....", "X....", "X...."],
    "G": [".XXXX", "X....", "X....", "X.XXX", "X...X", "X...X", ".XXX."],
    "H": ["X...X", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"],
    "I": ["XXXXX", "..X..", "..X..", "..X..", "..X..", "..X..", "XXXXX"],
    "J": ["..XXX", "...X.", "...X.", "...X.", "X..X.", "X..X.", ".XX.."],
    "K": ["X...X", "X..X.", "X.X..", "XX...", "X.X..", "X..X.", "X...X"],
    "L": ["X....", "X....", "X....", "X....", "X....", "X....", "XXXXX"],
    "M": ["X...X", "XX.XX", "X.X.X", "X.X.X", "X...X", "X...X", "X...X"],
    "N": ["X...X", "XX..X", "XX..X", "X.X.X", "X..XX", "X..XX", "X...X"],
    "O": [".XXX.", "X...X", "X...X", "X...X", "X...X", "X...X", ".XXX."],
    "P": ["XXXX.", "X...X", "X...X", "XXXX.", "X....", "X....", "X...."],
    "Q": [".XXX.", "X...X", "X...X", "X...X", "X.X.X", "X..X.", ".XX.X"],
    "R": ["XXXX.", "X...X", "X...X", "XXXX.", "X.X..", "X..X.", "X..X."],
    "S": [".XXXX", "X....", "X....", ".XXX.", "....X", "....X", "XXXX."],
    "T": ["XXXXX", "..X..", "..X..", "..X..", "..X..", "..X..", "..X.."],
    "U": ["X...X", "X...X", "X...X", "X...X", "X...X", "X...X", ".XXX."],
    "V": ["X...X", "X...X", "X...X", "X...X", "X...X", ".X.X.", "..X.."],
    "W": ["X...X", "X...X", "X...X", "X.X.X", "X.X.X", "XX.XX", "X...X"],
    "X": ["X...X", "X...X", ".X.X.", "..X..", ".X.X.", "X...X", "X...X"],
    "Y": ["X...X", "X...X", ".X.X.", "..X..", "..X..", "..X..", "..X.."],
    "Z": ["XXXXX", "....X", "...X.", "..X..", ".X...", "X....", "XXXXX"],
    "0": [".XXX.", "X...X", "X...X", "X...X", "X...X", "X...X", ".XXX."],
    "1": ["..X..", ".XX..", "..X..", "..X..", "..X..", "..X..", ".XXX."],
    "2": [".XXX.", "X...X", "....X", "...X.", "..X..", ".X...", "XXXXX"],
    "3": ["XXXX.", "....X", "....X", ".XXX.", "....X", "....X", "XXXX."],
    "4": ["...X.", "..XX.", ".X.X.", "X..X.", "XXXXX", "...X.", "...X."],
    "5": ["XXXXX", "X....", "XXXX.", "....X", "....X", "X...X", ".XXX."],
    "6": [".XXX.", "X....", "X....", "XXXX.", "X...X", "X...X", ".XXX."],
    "7": ["XXXXX", "....X", "...X.", "..X..", ".X...", ".X...", ".X..."],
    "8": [".XXX.", "X...X", "X...X", ".XXX.", "X...X", "X...X", ".XXX."],
    "9": [".XXX.", "X...X", "X...X", ".XXXX", "....X", "....X", ".XXX."],
}


def draw_glyph(d, x, y, ch, scale, color):
    glyph = FONT.get(ch, FONT.get("X"))
    for j, row in enumerate(glyph):
        for i, c in enumerate(row):
            if c == "X":
                x0, y0 = x + i * scale, y + j * scale
                d.rectangle([x0, y0, x0 + scale - 1, y0 + scale - 1],
                            fill=color)


def vgrad(size, c1, c2):
    """Vertical gradient image from c1 (top) to c2 (bottom)."""
    g = Image.new("RGB", size)
    d = ImageDraw.Draw(g)
    h = size[1]
    for y in range(h):
        t = y / max(1, h - 1)
        d.line([(0, y), (size[0], y)],
               fill=tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)))
    return g


def build(letter, size, c1, c2):
    s = size
    img = Image.new("RGB", (s, s), BG)
    # Gradient ring: outer disc minus inner disc used as mask.
    ring_outer = int(s * 0.44)
    ring_w = max(2, int(s * 0.045))
    mask = Image.new("L", (s, s), 0)
    dm = ImageDraw.Draw(mask)
    dm.ellipse([s / 2 - ring_outer, s / 2 - ring_outer,
                s / 2 + ring_outer, s / 2 + ring_outer], fill=255)
    ri = ring_outer - ring_w
    dm.ellipse([s / 2 - ri, s / 2 - ri,
                s / 2 + ri, s / 2 + ri], fill=0)
    img.paste(vgrad((s, s), c1, c2), (0, 0), mask)
    # Inner badge disc (dark) to seat the letter.
    d = ImageDraw.Draw(img)
    inner = int(s * 0.36)
    d.ellipse([s / 2 - inner, s / 2 - inner,
               s / 2 + inner, s / 2 + inner], fill=(16, 19, 26))
    # Gradient underline bar for style.
    bar_w, bar_h = int(s * 0.4), max(2, s // 64)
    bar = vgrad((bar_w, bar_h), c1, c2) if bar_h > 1 else None
    # Center the letter glyph.
    scale = max(1, s // 64)  # pixel size of one font cell
    gw, gh = 5 * scale, 7 * scale
    gx, gy = (s - gw) // 2, (s - gh) // 2 - bar_h
    draw_glyph(d, gx, gy, letter, scale, WHITE)
    if bar is not None:
        img.paste(bar, ((s - bar_w) // 2, gy + gh + scale * 2))
    return img


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Generate letter avatar PNG")
    p.add_argument("--letter", default="S",
                   help="Single letter or digit for the emblem")
    p.add_argument("--out", default="pfp.png", help="Output PNG path")
    p.add_argument("--size", type=int, default=512,
                   help="Width/height in pixels")
    p.add_argument("--theme", default="violet-cyan", choices=sorted(THEMES),
                   help="Color theme")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    letter = (args.letter or "S").strip().upper()[:1] or "S"
    if letter not in FONT:
        print("warning: %r not in font, using 'X'" % letter)
        letter = "X"
    if args.size < 64 or args.size > 2048:
        print("ERROR: --size must be 64..2048", file=sys.stderr)
        sys.exit(2)
    c1, c2 = THEMES[args.theme]
    img = build(letter, args.size, c1, c2)
    out = Path(args.out)
    if out.parent != Path(".") and str(out.parent):
        out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print("saved", out)


if __name__ == "__main__":
    main()
