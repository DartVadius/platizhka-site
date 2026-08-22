#!/usr/bin/env python3
"""Render the Open Graph share images — one per language.

Why these exist: without og:image a link to the site unfurls in Telegram, Viber
and Facebook as bare text. For a product that spreads hand to hand that is the
difference between a card people notice and a line they skip.

Why one per language rather than one shared image: the card carries a sentence,
and og:title is already per-language, so a Ukrainian reader sharing the
Ukrainian page should not unfurl a card in English.

    python3 tool/make_og_images.py

Requires headless Chrome (macOS path below) — this is a build-time tool, not
part of build.py, and its output is committed. Re-run it only when the wording,
the palette or the screenshot changes.
"""

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# 1200x630 is the size every scraper crops to 1.91:1 without letterboxing.
W, H = 1200, 630

COPY = {
    "uk": ("Комунальні платежі<br>без паперу й таблиць",
           "Android · безкоштовно · працює офлайн"),
    "ru": ("Коммунальные платежи<br>без бумаги и таблиц",
           "Android · бесплатно · работает офлайн"),
    "en": ("Utility bills without<br>paper or spreadsheets",
           "Android · free · works offline"),
}

PAGE = """<!doctype html>
<meta charset="utf-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: %(w)dpx; height: %(h)dpx; overflow: hidden; }
  body {
    display: flex; align-items: center; gap: 3rem;
    padding: 0 0 0 4.5rem;
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    color: #fff;
    background:
      radial-gradient(40rem 30rem at 12%% 18%%, rgba(255,255,255,.20), transparent 62%%),
      radial-gradient(32rem 26rem at 92%% 88%%, rgba(23,193,199,.28), transparent 65%%),
      linear-gradient(135deg, #1E4CB3 0%%, #2f5ecb 52%%, #3D6FE0 100%%);
  }
  .col { flex: 1 1 auto; min-width: 0; }
  .brand { display: flex; align-items: center; gap: .85rem; margin-bottom: 2.1rem; }
  .mark {
    width: 62px; height: 62px; border-radius: 17px;
    background: rgba(255,255,255,.16);
    border: 1px solid rgba(255,255,255,.30);
    display: grid; place-items: center;
    font-size: 34px; font-weight: 700; line-height: 1;
  }
  .name { font-size: 40px; font-weight: 800; letter-spacing: -.02em; }
  h1 {
    font-size: 62px; line-height: 1.1; font-weight: 800;
    letter-spacing: -.03em; text-wrap: balance;
  }
  .foot {
    margin-top: 2.2rem; font-size: 25px; font-weight: 500;
    color: rgba(255,255,255,.82); letter-spacing: .01em;
  }
  /* The phone bleeds off the bottom edge: a fully contained screenshot at this
     canvas size ends up too small to read, and the crop reads as intentional. */
  .shot { flex: 0 0 auto; align-self: flex-end; margin-right: 4.5rem; }
  .shot img {
    display: block; width: 268px; height: auto;
    margin-bottom: -46px;
    border-radius: 22px 22px 0 0;
    border: 1px solid rgba(255,255,255,.22);
    box-shadow: 0 34px 70px -18px rgba(6,14,34,.60);
  }
</style>
<div class="col">
  <div class="brand">
    <div class="mark">%(mark)s</div>
    <div class="name">%(brand)s</div>
  </div>
  <h1>%(headline)s</h1>
  <div class="foot">%(foot)s</div>
</div>
<div class="shot"><img src="%(shot)s"></div>
"""


def main():
    with open(os.path.join(ROOT, "content", "site.json"), encoding="utf-8") as fh:
        cfg = json.load(fh)
    if not os.path.exists(CHROME):
        sys.exit("headless Chrome not found at %s" % CHROME)

    shot = "file://" + os.path.join(ROOT, "assets", "img", "screen-home@2x.png")
    tmp = os.path.join(ROOT, ".og-tmp")
    os.makedirs(tmp, exist_ok=True)
    try:
        for lang in cfg["langs"]:
            headline, foot = COPY[lang]
            html = PAGE % {"w": W, "h": H, "mark": cfg["mark"], "brand": cfg["brand"],
                           "headline": headline, "foot": foot, "shot": shot}
            src = os.path.join(tmp, "og-%s.html" % lang)
            with open(src, "w", encoding="utf-8") as fh:
                fh.write(html)
            out = os.path.join(ROOT, "assets", "img", "og-%s.png" % lang)
            subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                            "--force-device-scale-factor=1",
                            "--window-size=%d,%d" % (W, H),
                            "--screenshot=" + out, "file://" + src],
                           check=True, capture_output=True)
            print("  assets/img/og-%s.png  %d KB" % (lang, os.path.getsize(out) // 1024))
    finally:
        for name in os.listdir(tmp):
            os.remove(os.path.join(tmp, name))
        os.rmdir(tmp)


if __name__ == "__main__":
    main()
