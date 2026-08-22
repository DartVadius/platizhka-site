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
