#!/usr/bin/env python3
"""Build social-media brand assets from the official SPM logo files.

Run with a Python environment that provides Pillow. The static site build uses
the generated PNG files and does not invoke this script.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
LOGO_DIR = ROOT / "assets" / "logo"
OUTPUT_DIR = ROOT / "assets" / "social"


def contain(image: Image.Image, width: int, height: int) -> Image.Image:
    result = image.copy()
    result.thumbnail((width, height), Image.Resampling.LANCZOS)
    return result


def build_avatar(mark: Image.Image) -> None:
    canvas = Image.new("RGB", (1024, 1024), "#F7F9FE")
    draw = ImageDraw.Draw(canvas)
    draw.ellipse((38, 38, 986, 986), fill="#FFFFFF", outline="#E4E9F4", width=4)
    safe_mark = contain(mark, 720, 720)
    position = (
        (canvas.width - safe_mark.width) // 2,
        (canvas.height - safe_mark.height) // 2,
    )
    canvas.paste(safe_mark, position, safe_mark)
    canvas.save(OUTPUT_DIR / "spmos-x-avatar.png", optimize=True)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    mark = Image.open(LOGO_DIR / "orbit-mark-light.webp").convert("RGBA")
    build_avatar(mark)
    print(OUTPUT_DIR / "spmos-x-avatar.png")


if __name__ == "__main__":
    main()
