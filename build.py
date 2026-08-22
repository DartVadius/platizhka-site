#!/usr/bin/env python3
"""Static site generator for platizhka.com.ua — standard library only.

Content lives as HTML fragments with a small `key: value` header. This script
wraps them in the shared chrome and derives everything that must not be
maintained by hand: per-page metadata, hreflang clusters, JSON-LD, the blog
indexes, sitemap.xml and llms.txt.

Why a generator at all, given "static, no backend": three languages times one
or two articles a week is three to six new files weekly with identical head and
header markup. Hand-copying that guarantees drift in exactly the fields that
matter for search. The output is still plain static HTML — GitHub Pages never
runs this script.

    python3 build.py

Deliberately not using Markdown: a hand-rolled parser is a source of silent
formatting bugs, and articles are written once. Fragments are HTML.
"""

import html
import json
import os
import re
import shutil
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(ROOT, "content", "site.json"), encoding="utf-8") as _fh:
    CFG = json.load(_fh)

SITE = CFG["site"].rstrip("/")
LANGS = CFG["langs"]
ROOT_LANG = CFG["root_lang"]
UI = CFG["ui"]

# The root language serves "/" — GitHub Pages cannot redirect, so the root has
# to hold real content rather than bounce somewhere.
PREFIX = {lang: ("" if lang == ROOT_LANG else "/" + lang) for lang in LANGS}

# ⚠ Bare language codes on purpose. Region codes are one of the three mistakes
# Google names for hreflang, and they are easy to get wrong here: "ru-RU" would
# target users *in Russia*, while our Russian-speaking readers are in Ukraine.
# Language-only annotations target the language wherever the reader is.
HREF_TAG = {lang: lang for lang in LANGS}
OG_LOCALE = {"uk": "uk_UA", "ru": "ru_RU", "en": "en_US",
             "de": "de_DE", "fr": "fr_FR", "es": "es_ES", "pt": "pt_PT"}


# Filled by main() before anything renders: per-language URLs that the chrome
# needs but cannot derive on its own, because whether a page exists in a given
# language is only known after the content directory has been scanned.
LINKS = {}


def analytics_snippet():
    """The Cloudflare Web Analytics beacon, or nothing if no token is set.

    Cookieless by design — Cloudflare states it uses no client-side state and
    does not fingerprint by IP or User-Agent — so this needs no consent banner.
    What it still needs is a line in the privacy page, which is why that page
    exists.

    Host-guarded on purpose: a `python3 -m http.server` preview would otherwise
    report into the same dashboard, and at our traffic volume a dozen localhost
    page views is not noise around the signal, it *is* the chart.
    """
    token = CFG.get("cf_beacon_token", "").strip()
    if not token:
        return ""
    if not re.fullmatch(r"[0-9a-f]{16,64}", token):
        raise SystemExit("cf_beacon_token does not look like a Cloudflare token: %r" % token)
    return ("""<script>
/* Cloudflare Web Analytics. No cookies, no localStorage, no fingerprinting,
   therefore no consent banner; disclosed on the privacy page all the same. */
if (location.hostname === %s) {
  var b = document.createElement('script');
  b.type = 'module';
  b.src = 'https://static.cloudflareinsights.com/beacon.min.js';
  b.setAttribute('data-cf-beacon', '{"token":"%s"}');
  document.head.appendChild(b);
}
</script>""" % (json.dumps(SITE.split("//", 1)[1]), token))


ANALYTICS = analytics_snippet()


def read_fragment(path):
    """Split a content file into a `key: value` header and an HTML body."""
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    if "\n---\n" not in raw:
        raise SystemExit("%s: missing '---' separator between header and body" % path)
    head, body = raw.split("\n---\n", 1)
    meta = {}
    for line in head.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise SystemExit("%s: header line without a colon: %r" % (path, line))
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    return meta, body.strip()


PER_PAGE = 10  # posts per index page

# `kind:` in an article header decides which section it lands in, and therefore
# its URL. "guide" is the default so existing articles keep their addresses.
SECTIONS = ["blog", "news"]
KIND_SECTION = {"guide": "blog", "news": "news"}


def url_for(lang, rel):
    """rel is '' for home, 'blog' for the index, 'blog/page/2' for page two,
    'blog/<slug>' for a post."""
    part = ("/" + rel).rstrip("/")
    return (PREFIX[lang] + part + "/").replace("//", "/") or "/"


def hreflang_block(rel, available):
    """Every page links to its own translations — not to the home page."""
    out = []
    for lang in LANGS:
        if lang in available:
            out.append('<link rel="alternate" hreflang="%s" href="%s%s">'
                       % (HREF_TAG[lang], SITE, url_for(lang, rel)))
    if ROOT_LANG in available:
        out.append('<link rel="alternate" hreflang="x-default" href="%s%s">'
                   % (SITE, url_for(ROOT_LANG, rel)))
    return "\n".join(out)


def langswitch(rel, available, current):
    out = []
    for lang in LANGS:
        if lang not in available:
            continue
        cur = ' aria-current="true"' if lang == current else ""
        out.append('<a href="%s" hreflang="%s" lang="%s"%s>%s</a>'
                   % (url_for(lang, rel), HREF_TAG[lang], lang, cur, lang))
    return "".join(out)


def render(template, lang, rel, available, meta, body, jsonld,
           og_type="website", nav=""):
    t = UI[lang]
    page = template
    subs = {
        # BODY first on purpose: content fragments may use {{BLOG}} or
        # {{INSTALL_URL}}, and the loop below is ordered, so the body has to be
        # in place before the rest of the substitutions run over it.
        "BODY": body,
        "LANG": lang,
        "THEME_ATTR": "",
        "TITLE": html.escape(meta["title"], quote=True),
        "DESCRIPTION": html.escape(meta["description"], quote=True),
        "CANONICAL": SITE + url_for(lang, rel),
        "HREFLANG": hreflang_block(rel, available),
        "OG_TYPE": og_type,
        "OG_TITLE": html.escape(meta.get("og_title", meta["title"]), quote=True),
        "OG_LOCALE": OG_LOCALE.get(lang, lang),
        # Absolute URL on purpose: the OG spec requires it and scrapers do not
        # resolve relative paths. Per-language because the card carries a
        # sentence — see tool/make_og_images.py.
        "OG_IMAGE": "%s/assets/img/og-%s.png" % (SITE, lang),
        "OG_IMAGE_ALT": html.escape(meta.get("og_title", meta["title"]), quote=True),
        "JSONLD": json.dumps(jsonld, ensure_ascii=False, separators=(",", ":")),
        "HOME": url_for(lang, ""),
        "BLOG": url_for(lang, "blog"),
        "NAV": nav,
        "LANGSWITCH": langswitch(rel, available, lang),
        "L_NAV": t["nav"],
        "L_THEME": t["theme"], "L_PRIVACY": t["privacy"],
        "BRAND": CFG["brand"], "MARK": CFG["mark"],
        "CONTACT": CFG["contact"], "PRIVACY_URL": CFG["privacy_url"],
        # The site's own privacy page when it exists in this language, else the
        # app's policy — a footer link must never point at a 404.
        "PRIVACY_PAGE": LINKS.get("privacy:" + lang, CFG["privacy_url"]),
        "ANALYTICS": ANALYTICS,
        "INSTALL_URL": CFG["install_url"], "YEAR": str(date.today().year),
    }
    for name, svg in ICONS.items():
        subs["ICON_" + name.upper()] = svg
    for key, value in subs.items():
        page = page.replace("{{%s}}" % key, value)
    left = re.findall(r"\{\{([A-Z_]+)\}\}", page)
    if left:
        raise SystemExit("unresolved placeholders: %s" % sorted(set(left)))
    return page


def write(rel_path, text):
    dest = os.path.join(ROOT, rel_path.lstrip("/"))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(text)
    return dest


# ── inline icon set ──────────────────────────────────────────────────────
# Hand-drawn line icons rather than emoji: emoji render differently on every
# OS, so a row of them never looks like a set. These share one grid, one stroke
# weight and inherit `currentColor`, so they follow the theme. Kept here rather
# than in the content because six icons across three languages would otherwise
# be eighteen copies to keep in sync.
_SVG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" '
        'aria-hidden="true">%s</svg>')

ICONS = {
    # stepped bars — consumption blocks, the whole point of a tiered tariff
    "tariffs": _SVG % ('<path d="M3 20h18"/><path d="M6 20v-4h4v4"/>'
                       '<path d="M10 16v-5h4v9"/><path d="M14 11V6h4v14"/>'),
    # stacked months with a lock: saved history that cannot be rewritten
    "history": _SVG % ('<rect x="3" y="8" width="12" height="12" rx="2"/>'
                       '<path d="M6 5h12M8 2.5h12"/>'
                       '<rect x="15.5" y="14" width="6" height="5" rx="1.2"/>'
                       '<path d="M17 14v-1.5a1.5 1.5 0 0 1 3 0V14"/>'),
    # two buildings of different height — several addresses
    "addresses": _SVG % ('<path d="M3 21V9l6-4v16"/><path d="M9 21V11l6 3v7"/>'
                         '<path d="M15 21V14l6 3v4"/><path d="M2 21h20"/>'
                         '<path d="M6 12h.01M6 16h.01M12 16h.01"/>'),
    # bell with a chime mark — the monthly reminder
    "reminder": _SVG % ('<path d="M18 9a6 6 0 1 0-12 0c0 5-2 6-2 6h16s-2-1-2-6"/>'
                        '<path d="M10.5 19a2 2 0 0 0 3 0"/>'),
    # crossed-out cloud — no servers, works with the network off
    "offline": _SVG % ('<path d="M17.5 18H7a4 4 0 0 1-.4-7.98"/>'
                       '<path d="M9 7.2A5 5 0 0 1 18 9.5v.5a3.5 3.5 0 0 1 1.8 6.3"/>'
                       '<path d="M3 3l18 18"/>'),
    # card with a slash — no purchases, nothing to cancel
    "free": _SVG % ('<rect x="2.5" y="5.5" width="19" height="13" rx="2.5"/>'
                    '<path d="M2.5 10h19"/><path d="M4 3l16 18"/>'),
}


def build_nav(lang, sections_present):
    """Only link sections that actually have a page in this language.

    A section with nothing in it is a thin page and a dead nav entry, so the
    news archive simply does not exist until the first news post lands. That is
    what makes it a placeholder that costs nothing while empty.
    """
    t = UI[lang]
    out = ['<a class="navlink" href="%s">%s</a>' % (url_for(lang, ""), t["app"])]
    for section in SECTIONS:
        if section in sections_present:
            out.append('<a class="navlink" href="%s">%s</a>'
                       % (url_for(lang, section), t[section_label(section)]))
    return "".join(out)


def section_label(section):
    return "blog" if section == "blog" else section


def app_jsonld(lang):
    """The app itself. `SoftwareApplication` is what both search engines and
    answer engines read to state what the thing is, for free, and on what."""
    return {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": CFG["brand"],
        "applicationCategory": CFG["app_category"],
        "operatingSystem": CFG["app_os"],
        "url": SITE + url_for(lang, ""),
        "installUrl": CFG["install_url"],
        "inLanguage": LANGS,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "UAH"},
        "author": {"@type": "Person", "name": CFG["author"]},
    }


def main():
    with open(os.path.join(ROOT, "templates", "base.html"), encoding="utf-8") as fh:
        template = fh.read()

    # ── collect posts: slug -> {lang: (meta, body)} ────────────────────
    posts = {}
    for lang in LANGS:
        d = os.path.join(ROOT, "content", lang, "blog")
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if not name.endswith(".html"):
                continue
            slug = name[:-5]
            meta, body = read_fragment(os.path.join(d, name))
            for field in ("title", "description", "date", "summary"):
                if field not in meta:
                    raise SystemExit("%s/%s: header is missing '%s'" % (lang, name, field))
            section = KIND_SECTION.get(meta.get("kind", "guide"))
            if section is None:
                raise SystemExit("%s/%s: unknown kind %r (use guide or news)"
                                 % (lang, name, meta.get("kind")))
            posts.setdefault(slug, {})[lang] = (meta, body, section)

    # Sections present per language — computed first, because the header nav on
    # *every* page depends on it, including the home page.
    present = {lang: set() for lang in LANGS}
    for slug, per in posts.items():
        for lang, (_m, _b, section) in per.items():
            present[lang].add(section)
    navs = {lang: build_nav(lang, present.get(lang, set())) for lang in LANGS}

    # ── standalone pages ───────────────────────────────────────────────
    # content/<lang>/pages/<slug>.html becomes /<slug>/. For anything that is
    # neither the home page nor an article — privacy, and later about or terms.
    # Deliberately absent from the nav: these are footer pages, linked from
    # where they are actually needed, so they do not compete for header space.
    # Scanned before rendering because the footer link on *every* page depends
    # on which languages have the privacy page at all.
    standalone = {}
    for lang in LANGS:
        d = os.path.join(ROOT, "content", lang, "pages")
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if name.endswith(".html"):
                standalone.setdefault(name[:-5], {})[lang] = os.path.join(d, name)

    for lang in standalone.get("privacy", {}):
        LINKS["privacy:" + lang] = url_for(lang, "privacy")

    built = []

    # ── home pages ─────────────────────────────────────────────────────
    home_langs = [l for l in LANGS
                  if os.path.exists(os.path.join(ROOT, "content", l, "index.html"))]
    for lang in home_langs:
        meta, body = read_fragment(os.path.join(ROOT, "content", lang, "index.html"))
        jsonld = {"@context": "https://schema.org", "@graph": [
            app_jsonld(lang),
            {"@type": "WebSite", "name": CFG["brand"], "url": SITE + url_for(lang, ""),
             "inLanguage": lang},
        ]}
        page = render(template, lang, "", home_langs, meta, body, jsonld,
                      nav=navs[lang])
        built.append((url_for(lang, ""), write(url_for(lang, "") + "index.html", page)))

    # ── section indexes, paginated ─────────────────────────────────────
    # Pagination is wired up from the start even though one post does not need
    # it: the URL of page 2 has to be decided before it exists, because Pages
    # cannot redirect and a moved URL loses whatever it earned. Page 1 stays at
    # /<section>/ forever; later pages are /<section>/page/N/.
    #
    # hreflang here is per *section and page number*: languages accumulate posts
    # at different rates, so /blog/page/3/ may exist in Ukrainian and not in
    # English. Announcing a page that 404s makes Google drop the annotation.
    pages_by = {}
    for section in SECTIONS:
        for lang in home_langs:
            items = [(slug, per[lang][0], per[lang][1])
                     for slug, per in posts.items()
                     if lang in per and per[lang][2] == section]
            items.sort(key=lambda it: it[1]["date"], reverse=True)
            if not items:
                continue
            pages_by[(section, lang)] = [items[i:i + PER_PAGE]
                                         for i in range(0, len(items), PER_PAGE)]

    for (section, lang), chunks in sorted(pages_by.items()):
        t = UI[lang]
        total = len(chunks)
        label = t[section_label(section)]
        title_key = "blog_title" if section == "blog" else "news_title"
        desc_key = "blog_desc" if section == "blog" else "news_desc"
        for idx, chunk in enumerate(chunks, start=1):
            rel = section if idx == 1 else "%s/page/%d" % (section, idx)
            available = [l for (sec, l), ch in pages_by.items()
                         if sec == section and len(ch) >= idx]

            rows = []
            for slug, meta, _body in chunk:
                kind = meta.get("kind", "guide")
                cls = " kind--news" if kind == "news" else ""
                stamp = meta.get("updated", meta["date"])
                rows.append(
                    '<li><a href="%s"><span class="meta">'
                    '<span class="kind%s">%s</span>%s</span>'
                    '<h2>%s</h2><p>%s</p></a></li>'
                    % (url_for(lang, section + "/" + slug), cls,
                       html.escape(t.get("kind_" + kind, kind)), stamp,
                       html.escape(meta["title"]), html.escape(meta["summary"])))
            listing = '<ul class="postlist">%s</ul>' % "".join(rows)

            # Numbered links, always crawlable anchors — Google dropped
            # rel=next/prev, so plain links are what it reads now.
            pager = ""
            if total > 1:
                bits = []
                if idx > 1:
                    prev = section if idx == 2 else "%s/page/%d" % (section, idx - 1)
                    bits.append('<a rel="prev" href="%s">←</a>' % url_for(lang, prev))
                for n in range(1, total + 1):
                    href = url_for(lang, section if n == 1 else "%s/page/%d" % (section, n))
                    if n == idx:
                        bits.append('<span aria-current="page">%d</span>' % n)
                    else:
                        bits.append('<a href="%s">%d</a>' % (href, n))
                if idx < total:
                    bits.append('<a class="pager__side" rel="next" href="%s">→</a>'
                                % url_for(lang, "%s/page/%d" % (section, idx + 1)))
                pager = '<nav class="pager" aria-label="%s">%s</nav>' % (label, "".join(bits))

            suffix = "" if idx == 1 else " — %s %d" % (t.get("page", "page"), idx)
            index_meta = {"title": t[title_key] + suffix, "description": t[desc_key]}
            body = ('<div class="shell"><section><h1>%s</h1>'
                    '<p class="prose">%s</p>%s%s</section></div>'
                    % (label + suffix, html.escape(t[desc_key]), listing, pager))
            jsonld = {"@context": "https://schema.org", "@type": "Blog",
                      "name": index_meta["title"], "url": SITE + url_for(lang, rel),
                      "inLanguage": lang,
                      # author is required for BlogPosting — it is present on the
                      # articles themselves and was missing only here, which is
                      # what Ahrefs flagged as a rich-results error on all three
                      # section indexes.
                      "blogPost": [{"@type": "BlogPosting",
                                    "headline": m["title"],
                                    "datePublished": m["date"],
                                    "author": {"@type": "Person", "name": CFG["author"]},
                                    "url": SITE + url_for(lang, section + "/" + sl)}
                                   for sl, m, _b in chunk]}
            page = render(template, lang, rel, available, index_meta, body, jsonld,
                          nav=navs[lang])
            built.append((url_for(lang, rel), write(url_for(lang, rel) + "index.html", page)))

    # ── posts ──────────────────────────────────────────────────────────
    for slug, per in sorted(posts.items()):
        available = [l for l in LANGS if l in per]
        for lang in available:
            meta, body, section = per[lang]
            t = UI[lang]
            rel = section + "/" + slug
            label = t[section_label(section)]
            crumbs = ('<div class="shell crumbs"><a href="%s">%s</a> / <a href="%s">%s</a></div>'
                      % (url_for(lang, ""), t["home"], url_for(lang, section), label))

            kind = meta.get("kind", "guide")
            cls = " kind--news" if kind == "news" else ""
            stamp = meta["date"]
            if meta.get("updated") and meta["updated"] != meta["date"]:
                stamp = "%s · %s %s" % (meta["date"], t.get("updated", "updated"),
                                        meta["updated"])
            head = ('<div class="shell posthead prose"><p class="meta">'
                    '<span class="kind%s">%s</span>%s</p><h1>%s</h1></div>'
                    % (cls, html.escape(t.get("kind_" + kind, kind)), stamp,
                       html.escape(meta["title"])))
            tail = ('<div class="shell"><p><a class="btn btn--ghost" href="%s">%s</a></p></div>'
                    % (url_for(lang, section), t["back"] if section == "blog" else label))
            article = ('%s%s<article class="shell prose">%s</article>%s'
                       % (crumbs, head, body, tail))
            jsonld = {"@context": "https://schema.org", "@graph": [
                {"@type": "BlogPosting",
                 "headline": meta["title"],
                 "description": meta["description"],
                 "datePublished": meta["date"],
                 "dateModified": meta.get("updated", meta["date"]),
                 "inLanguage": lang,
                 "mainEntityOfPage": SITE + url_for(lang, rel),
                 "author": {"@type": "Person", "name": CFG["author"]},
                 "publisher": {"@type": "Organization", "name": CFG["brand"]},
                 "isPartOf": {"@type": "Blog", "url": SITE + url_for(lang, section)}},
                {"@type": "BreadcrumbList", "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": t["home"],
                     "item": SITE + url_for(lang, "")},
                    {"@type": "ListItem", "position": 2, "name": label,
                     "item": SITE + url_for(lang, section)},
                    {"@type": "ListItem", "position": 3, "name": meta["title"]},
                ]},
            ]}
            page = render(template, lang, rel, available, meta, article, jsonld,
                          og_type="article", nav=navs[lang])
            built.append((url_for(lang, rel), write(url_for(lang, rel) + "index.html", page)))

    for slug, per in sorted(standalone.items()):
        available = [l for l in LANGS if l in per]
        for lang in available:
            meta, body = read_fragment(per[lang])
            for field in ("title", "description"):
                if field not in meta:
                    raise SystemExit("%s/pages/%s: header is missing '%s'"
                                     % (lang, slug, field))
            jsonld = {"@context": "https://schema.org", "@type": "WebPage",
                      "name": meta["title"], "description": meta["description"],
                      "url": SITE + url_for(lang, slug), "inLanguage": lang}
            page = render(template, lang, slug, available, meta, body, jsonld,
                          nav=navs[lang])
            built.append((url_for(lang, slug),
                          write(url_for(lang, slug) + "index.html", page)))

    # ── sitemap ────────────────────────────────────────────────────────
    urls = "".join("<url><loc>%s%s</loc></url>" % (SITE, path) for path, _ in built)
    write("sitemap.xml",
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s</urlset>\n' % urls)

    # ── robots.txt ─────────────────────────────────────────────────────
    # Answer engines are allowed on purpose: being quoted by them is the point.
    write("robots.txt",
          "User-agent: *\nAllow: /\n\n"
          "# Answer engines are welcome — being cited is a goal, not a leak.\n"
          "User-agent: GPTBot\nAllow: /\n\n"
          "User-agent: ClaudeBot\nAllow: /\n\n"
          "User-agent: PerplexityBot\nAllow: /\n\n"
          "User-agent: Google-Extended\nAllow: /\n\n"
          "Sitemap: %s/sitemap.xml\n" % SITE)

    # ── llms.txt ───────────────────────────────────────────────────────
    # Emerging convention: a plain-text map for agents that would otherwise
    # guess at the site from markup. Cheap to keep, useless to nobody.
    lines = ["# " + CFG["brand"], "",
             "> " + CFG["agent_summary"], "",
             "Install: %s" % CFG["install_url"], "",
             "## Pages"]
    for path, _ in built:
        lines.append("- %s%s" % (SITE, path))
    write("llms.txt", "\n".join(lines) + "\n")

    # ── prune pages we generated before and no longer generate ─────────
    # Without this, deleting or renaming an article leaves the old page live
    # forever — and GitHub Pages cannot redirect it away. The manifest means we
    # only ever delete files this script created, never hand-written ones.
    manifest = os.path.join(ROOT, ".build-manifest")
    produced = sorted(os.path.relpath(dest, ROOT) for _, dest in built) + [
        "sitemap.xml", "robots.txt", "llms.txt"]
    previous = []
    if os.path.exists(manifest):
        with open(manifest, encoding="utf-8") as fh:
            previous = [ln.strip() for ln in fh if ln.strip()]

    removed = []
    for rel in previous:
        if rel in produced:
            continue
        dead = os.path.join(ROOT, rel)
        if os.path.isfile(dead):
            os.remove(dead)
            removed.append(rel)
            # take the directory with it if the page was its only content
            folder = os.path.dirname(dead)
            while folder != ROOT and os.path.isdir(folder) and not os.listdir(folder):
                os.rmdir(folder)
                folder = os.path.dirname(folder)

    with open(manifest, "w", encoding="utf-8") as fh:
        fh.write("\n".join(produced) + "\n")

    print("built %d pages:" % len(built))
    for path, _ in built:
        print("  ", path)
    if removed:
        print("removed %d stale page(s):" % len(removed))
        for rel in removed:
            print("  ", rel)


if __name__ == "__main__":
    main()
