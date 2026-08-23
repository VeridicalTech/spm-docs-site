#!/usr/bin/env python3
"""Build social-media brand assets from the official SPM logo files.

Run with a Python environment that provides Pillow. The static site build uses
the generated PNG files and does not invoke this script.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
LOGO_DIR = ROOT / "assets" / "logo"
OUTPUT_DIR = ROOT / "assets" / "social"
REGULAR_FONT_CANDIDATES = (
    Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
)
BOLD_FONT_CANDIDATES = (
    Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"),
)

INK = "#0B1020"
MUTED = "#505A6C"
BLUE = "#2D63F6"
PALE_BLUE = (239, 245, 255)
WHITE = (255, 255, 255)


def contain(image: Image.Image, width: int, height: int) -> Image.Image:
    result = image.copy()
    result.thumbnail((width, height), Image.Resampling.LANCZOS)
    return result


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def first_available(candidates: tuple[Path, ...]) -> Path:
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"No supported font found in: {candidates}")


def draw_tracking(
    draw: ImageDraw.ImageDraw,
    position: tuple[int, int],
    text: str,
    text_font: ImageFont.FreeTypeFont,
    fill: str,
    tracking: int,
) -> None:
    x, y = position
    for character in text:
        draw.text((x, y), character, font=text_font, fill=fill)
        x += int(draw.textlength(character, font=text_font)) + tracking


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


def build_report_card(lockup: Image.Image, mark: Image.Image) -> None:
    width, height = 1200, 630
    canvas = Image.new("RGB", (width, height), WHITE)
    pixels = canvas.load()
    for y in range(height):
        blend = y / (height - 1)
        for x in range(width):
            edge = max(0.0, (x - 680) / 520)
            amount = min(1.0, 0.12 * blend + 0.58 * edge)
            pixels[x, y] = tuple(
                round(WHITE[channel] * (1 - amount) + PALE_BLUE[channel] * amount)
                for channel in range(3)
            )

    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((44, 34, 1156, 596), radius=30, outline="#E3E8F2", width=2)
    draw.rounded_rectangle((66, 56, 412, 188), radius=20, fill="#FFFFFF")

    safe_lockup = contain(lockup, 310, 118)
    canvas.paste(safe_lockup, (84, 64), safe_lockup)

    safe_mark = contain(mark, 350, 350)
    mark_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    mark_layer.alpha_composite(safe_mark, (795, 150))
    mark_layer.putalpha(mark_layer.getchannel("A").point(lambda alpha: int(alpha * 0.90)))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), mark_layer).convert("RGB")
    draw = ImageDraw.Draw(canvas)

    regular_font = first_available(REGULAR_FONT_CANDIDATES)
    bold_font = first_available(BOLD_FONT_CANDIDATES)
    title_font = font(bold_font, 60)
    subtitle_font = font(regular_font, 25)
    label_font = font(bold_font, 16)
    url_font = font(bold_font, 20)

    draw.text((72, 228), "SPM-Polaris", font=title_font, fill=INK)
    draw.text((72, 294), "Technical Report", font=title_font, fill=INK)
    draw.multiline_text(
        (76, 382),
        "Evidence-governed memory and context management\nfor long-horizon AI agents",
        font=subtitle_font,
        fill=MUTED,
        spacing=10,
    )
    draw.rounded_rectangle((72, 493, 356, 531), radius=19, fill="#EAF0FF")
    draw_tracking(draw, (91, 503), "FIRST-PARTY · VERSION 1.0", label_font, BLUE, 1)
    draw.text((76, 552), "docs.spmos.ai/technical-report", font=url_font, fill=BLUE)
    draw.line((730, 548, 1122, 548), fill="#C8D5F5", width=2)

    canvas.save(OUTPUT_DIR / "spmos-technical-report-social.png", optimize=True)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    mark = Image.open(LOGO_DIR / "orbit-mark-light.webp").convert("RGBA")
    lockup = Image.open(LOGO_DIR / "orbit_light_upscaled.webp").convert("RGBA")
    build_avatar(mark)
    build_report_card(lockup, mark)
    print(OUTPUT_DIR / "spmos-x-avatar.png")
    print(OUTPUT_DIR / "spmos-technical-report-social.png")


if __name__ == "__main__":
    main()
