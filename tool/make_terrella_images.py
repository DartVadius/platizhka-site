#!/usr/bin/env python3
"""Images for the Terrella announcement (content/<lang>/blog/terrella.html).

Takes Terrella's ENGLISH Play Store screenshots (1080x1920, already cropped to
9:16 by globus/tool/crop_screenshot.py) and writes:

  assets/img/terrella/{political,historical,stars}.webp   480x853, one set for every language
  assets/img/terrella/og-<lang>.png                       1200x630 share card per language

    python3 tool/make_terrella_images.py [lang ...]

⚠ One set of shots for all three articles, in English (owner, 2026-10-17: «не надо
отдельные скриншоты — бери английские и тех что мы для гугло плея делали»). The
share card stays per language: its tagline is text in the article's language.

Output is committed, like tool/make_og_images.py: re-run only when a store
screenshot changes. The fonts are Terrella's own, read from the sibling project.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "img", "terrella")
FONTS = os.path.join(ROOT, "..", "globus", "assets", "fonts")
STORE = os.path.join(ROOT, "..", "globus", "publishing", "store-listing", "graphics",
                     "screenshots")
BG = (5, 7, 12)                      # Terrella's background, sampled from a capture
# article name → the store screenshot it is made from
SHOTS = {"political": "en-1-political.png", "historical": "en-4-historical.png",
         "stars": "en-2-stars.png"}

# The Play short descriptions' opening phrase, per language.
TAGLINE = {
    "uk": "Глобус у кишені",
    "ru": "Глобус в кармане",
    "en": "A globe in your pocket",
}


def shot(src, dst):
    """A 9:16 store screenshot down to 480x853 — the bars are already off."""
    im = Image.open(src).convert("RGB")
    assert im.size == (1080, 1920), f"{src}: expected a 1080x1920 store shot, got {im.size}"
    im.resize((480, 853), Image.LANCZOS).save(dst, "WEBP", quality=82, method=6)


def og_card(src, lang, dst):
    """Globe on the left fading into the background, name and tagline right —
    the layout of the Google Ads 1.91:1 images, at the 1200x630 OG size."""
    W, H = 1200, 630
    card = Image.new("RGB", (W, H), BG)
    im = Image.open(src).convert("RGB")
    # A square from the middle of the screen, stopping short of the mode strip:
    # the strip's buttons run down the right edge from x ≈ 890, and a share
    # card with app chrome in it reads as a screenshot rather than a picture.
    side = 880
    top = (im.height - side) // 2
    globe = im.crop((0, top, side, top + side)).resize((H, H), Image.LANCZOS)
    fade = Image.new("L", (H, H), 255)
    d = ImageDraw.Draw(fade)
    for x in range(H - 140, H):
        d.line([(x, 0), (x, H)], fill=int(255 * (H - x) / 140))
    card.paste(globe, (0, 0), fade)

    d = ImageDraw.Draw(card)
    name = ImageFont.truetype(os.path.join(FONTS, "Alegreya-Bold.ttf"), 112)
    tag = ImageFont.truetype(os.path.join(FONTS, "Alegreya-SemiBoldItalic.ttf"), 44)
    cx = H + (W - H) // 2
    for text, font, y, fill in [("Terrella", name, 230, (245, 240, 228)),
                                (TAGLINE[lang], tag, 375, (226, 170, 72))]:
        b = d.textbbox((0, 0), text, font=font)
        if b[2] - b[0] > W - H - 40:
            raise SystemExit("too wide for the card: %r" % text)
        d.text((cx - (b[2] - b[0]) // 2 - b[0], y), text, font=font, fill=fill)
    card.save(dst, optimize=True)


def main():
    langs = sys.argv[1:] or list(TAGLINE)
    os.makedirs(OUT, exist_ok=True)
    for name, src in SHOTS.items():
        shot(os.path.join(STORE, src), os.path.join(OUT, "%s.webp" % name))
    for lang in langs:
        og_card(os.path.join(STORE, SHOTS["political"]), lang,
                os.path.join(OUT, "og-%s.png" % lang))
        print("──", lang)


if __name__ == "__main__":
    main()
