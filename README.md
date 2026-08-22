# platizhka.com.ua

Static site for **Платіжка** — a utility-bill calculator for Android.
Hosted on GitHub Pages, custom domain `platizhka.com.ua`, free Let's Encrypt HTTPS.

## Why this site exists

Play Store search only reaches people who already decided they want an app. Web
search reaches them earlier — «як розрахувати комунальні платежі», «тариф
день-ніч як вважається». This site targets that, and hosts the explanations a
store listing has no room for.

## URL structure — decided once, do not change

GitHub Pages serves static files and **cannot issue redirects**. There is no
`.htaccess`, no 301. So a URL that ships is a URL we keep: moving a page later
means losing whatever it earned, with only a client-side hack as consolation.

- `/` — the app: what it does, link to Google Play
- `/<slug>/` — one article per topic. Flat, lowercase, hyphenated, **no dates and
  no category prefix** — dates make a page look stale and prefixes are a level we
  would have to live with forever.

## Language

Ukrainian only for now (`lang="uk"`). The audience is in Ukraine. A Russian
version doubles the writing and proofreading cost, so it waits until the traffic
data says it is worth it.

## Content rules

- **Explain mechanics, never publish tariff rates.** Rates are regional and
  change; mechanics hold for years. An article with prices is wrong within weeks.
- **Few strong pages, not many thin ones.** Google's spam policy names "many
  pages without adding value" as scaled content abuse — volume is the risk, not
  authorship.
- Facts get sources. The readers pay these bills and will catch an error faster
  than Google will.

## Deploy

Push to `main`. Pages settings: deploy from branch `main`, root. `CNAME` holds
the custom domain — do not delete it, GitHub reads it on every build.

## Adding an article

1. Create `content/<lang>/blog/<slug>.html`. The slug becomes the URL, so pick it
   once — see the URL rule above.
2. Start the file with a `key: value` header, then `---`, then the body as plain
   HTML (`<h2>`, `<p>`, `<ul>`, `<table>`, `.note` blocks). Required header keys:

   ```
   title:       used in <title>, <h1> and JSON-LD
   description: the meta description — one sentence, unique per page
   summary:     the teaser shown in the blog index
   date:        YYYY-MM-DD, also the sort key
   ```

   Optional: `og_title` (a shorter social headline), `updated` (YYYY-MM-DD).
3. Ukrainian is mandatory; `ru` and `en` are per-article. A translation that does
   not exist simply drops out of that article's hreflang cluster — the generator
   computes the cluster from the files that are actually there.
4. `python3 build.py` then `python3 notify.py` to ping IndexNow.
5. Commit both the content and the generated HTML. Pages serves what is committed.

⚠ Never machine-translate an article just to fill all three languages. Google's
spam policy targets "many pages without adding value"; three thin translations are
worse than one good article.

## Pagination

Ten posts per index page. Page 1 is `/blog/` forever; later pages are
`/blog/page/N/`. It engages by itself once a language passes ten posts — nothing to
configure. Each page canonicalises to itself (Google's guidance for paginated
series) and carries hreflang only for the languages that actually have that page
number, since languages accumulate posts at different rates.

## Reusing this for another product

`build.py`, `templates/` and `assets/style.css` contain nothing product-specific.
To stand up a second site (Terrella):

1. Copy `build.py`, `templates/`, `assets/style.css`, `assets/app.js`, `notify.py`.
2. Write a new `content/site.json`: domain, brand, install URL, `langs`,
   `root_lang`, and the UI strings per language. Terrella ships seven languages
   with English as the root language — the generator takes the list as data.
3. Generate a fresh IndexNow key: `python3 -c "import secrets;print(secrets.token_hex(16))"`,
   save it to `<key>.txt` in the site root and to `indexnow_key` in site.json.
4. Replace `assets/img/` and the favicon, then write content.

Do **not** merge the two products into one domain. The audiences share no
language, queries or reason to link, and topical coherence is a real ranking
factor — the reasoning is recorded in `komunalka/publishing/marketing.md`.

## Two kinds of article, and why the distinction matters

Set `kind:` in the header — `guide` (default) or `news`.

- **`guide`** — evergreen mechanics. No dates in the text, no tariff rates. Stays
  true for years, which is why it can accumulate ranking.
- **`news`** — legislation and tariff changes. Inherently dated, so it *must* carry
  a visible date, the date the change takes effect, and a link to the source. The
  generator prints the label and the date for you.

⚠ **For a recurring topic, update one article in place — do not publish a new URL
per change.** "Electricity tariffs" should be a single page whose `updated:` moves
forward, with superseded figures kept in a "how it was before" section. A new post
each time rates change produces a graveyard of stale URLs that GitHub Pages cannot
even redirect away, and splits the authority the topic earned across all of them.

⚠ **Never leave a price claim undated.** An article stating a rate without saying
as of when is the one thing that turns a useful site into an untrustworthy one —
and these readers pay those bills, so they will notice before Google does.
