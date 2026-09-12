# Promotion — what we target and why

Written 2026-08-29, when the site was a week old and had one article. Numbers
here are the ones actually measured that day; replace them, do not add to them.

## Do not wait for Search Console to tell you what to write

GSC reports the queries a site **already shows for**. With fifteen pages and
almost no index presence it reports a handful of accidents. Waiting for it to
produce a strategy is circular — you need content to get impressions,
impressions to get query data, and it is the content you are choosing.

It becomes useful in two or three months, and then for **refining**: which of
the clusters below actually caught. Not for choosing them.

⚠ Do not carry the opposite decision over from the app. Deferring the Play
listing rewrite until real query data existed was right, because the listing
already ranks and its ceiling is behavioural. The site is the mirror image: it
ranks for nothing yet.

## Two assets, two different mechanics

**The app — keyword work is essentially finished.** Measured by hand
2026-08-22: #1 «платіжка», #1 «калькулятор комунальных платежей», #3
«комунальні платежі», #6 «комуналка». «комунальні платежі» is already in the uk
title, the heaviest-weighted field there is, and still sits at 3 — that ceiling
is behavioural (installs, first opens, retention, ratings), and no wording
changes it. Promotion of the app is retention and reviews, not words.

**The site — nothing targeted yet.** This document is about the site.

## What the site can and cannot win

Head terms are unreachable: «комунальні платежі», «тарифи на електроенергію» and
the like are held by government portals, oblenergo and news sites with years of
authority. A domain with no weight loses there and wastes the attempt.

What is available is **question-shaped, mechanism-explaining queries** — how it
works, why the sum is what it is, what to do about it. Both existing articles
are that shape. It is not a consolation prize: for an unknown domain it is the
only viable route, and it is also what AI answer engines quote, which is what
`llms.txt` is there for.

## The clusters, in priority order

⚠ Priority is by **intent**, not by volume. The site exists to produce installs.
Someone typing "how do I calculate this myself" already wants what the app does;
someone typing "electricity tariff 2026" wants a number and leaves with it.

**A. Calculating it yourself — highest intent, lower volume.**
- як розрахувати комуналку самостійно
- як порахувати за електроенергію за показаннями
- як перевірити нарахування в платіжці

**B. Readings and meters — high volume, good intent.**
- як передати показання лічильника електроенергії
- до якого числа передавати показання
- що буде, якщо не передати показання ✅ published 2026-09-05
- смарт-лічильник: що це і як працює

**E. Water — opened 2026-09-12, was the blind spot below.**
- чому водовідведення дорівнює обсягу води ✅ published 2026-09-12
  (also covers: no readings for water, and meter verification)
- скільки коштує вода без лічильника / норми споживання
- як передати показання води

**C. Bills and recalculations — the surprise-driven searches.**
- перерахунок за електроенергію ✅ published 2026-08-29
- чому прийшов великий рахунок за електроенергію
- що таке абонплата за газ
- доставка газу окремим рядком

**D. Tariffs — highest volume, weakest fit.**
- чи вигідно переходити на двозонний лічильник
- двозонний тариф ✅ published 2026-08-22

⚠ «тарифи на електроенергію 2026» and its yearly siblings sit here and are
deliberately NOT planned. They draw the most traffic and they rot: every one
becomes a maintenance obligation, and a site this size cannot carry a shelf of
articles that must be re-checked each January.

## ⚠ Every cluster above was electricity, and nobody noticed — closed 2026-09-12

Counted 2026-09-05, at three published articles: of the thirteen planned topics
**eleven are electricity or service-neutral, two mention gas, none mention water.**
All three published articles are electricity. Owner: «кроме электричества, по
счётчику ещё воду и газ считают, надо будет в следующий раз сменить тип услуги».

**Why it happened.** Electricity is where the meter questions are richest — zones,
day/night, recalculations — so every topic that suggested itself was an electricity
topic. The app does not have that bias: it bills water, gas and heating on the same
eight tariff types.

**What it costs.** Someone searching «як рахують воду за лічильником» finds nothing of
ours, and the site looks like a tool for one utility rather than for the bill as a
whole.

⚠ **The articles cannot simply be relabelled.** The mechanics repeat — a missed
reading is estimated from your own average day for water and gas as well — but the
SOURCES do not: the electricity pieces cite the retail electricity market rules and
say «обленерго». A water version has to be sourced from the water-supply rules and
name the водоканал. Same shape, different research pass.

**Next article: change the utility, not the question.** The obvious pair to the one
just published is the same missed-reading mechanics for **water** — highest household
familiarity, zero coverage, and the one utility where a reading is submitted to a
different organisation than the one that bills.

✅ **Done 2026-09-12 — `/blog/voda-za-lichylnykom/`, all three languages.** The water
blind spot is closed, and the article turned out stronger than «the same question, a
different utility», which is worth recording:

- **The spine is a mechanic electricity does not have.** Clause 22 of the Rules
  (КМУ № 690 of 05.07.2019) sets the volume of водовідведення **equal to** the volume
  of water supplied plus hot water. One meter reading produces two charges, and the
  sewerage line has no lever of its own. That is a question people actually type, and
  no electricity article could have carried it.
- **Missed readings land on the NEIGHBOURS.** Clause 31: three months on the
  consumer's own average day over the previous 12 months (absent history, the actual
  period but not less than 15 days), then billing «as consumers whose premises are not
  equipped with distribution metering units» — i.e. by the local authority's norms. And
  once readings resume, the provider must redistribute the building's volume and
  recalculate **with every consumer in the building**. The electricity piece has no
  equivalent, because electricity is not distributed off a building meter this way.
- **Verification is a water-specific pain** and the answer is counter-intuitive:
  the flat's meter is a *distribution* unit, so ЗУ № 2119-VIII puts servicing and
  verification on the OWNER, unlike the building's commercial unit. At least once per
  six years for mechanical devices, nine for other types.

⚠ **The sources were read from the primary texts, not from a summary.** A first
research pass returned the three-month rule with «exact article numbers not
accessible», and one of its confident answers (who pays for verification) was the one I
most expected to be wrong — it turned out correct. Both were settled by pulling
zakon.rada's print view and quoting the clause. Do the same for the next one: these
readers pay these bills.

⚠ **Not decided — my suggestion, not the owner's call.** The remaining water topics in
cluster E (norms without a meter, how to submit a water reading) would deepen the
cluster; gas is the other untouched utility and already has two entries sitting in
cluster C. Whichever is next, the same rule applies: change the utility, keep the
question shape.

## English is a separate question

The audience is Ukrainian — over the 28 days to 2026-08-29 Ukraine grew 1→4
devices while Turkey, the USA, Germany and Zambia were the residue of
install-for-credit testers. English keyword lists (of the "water bill
calculator" kind an outreach email proposed) target an audience we do not have.

Where English earns its place is the **diaspora**: someone abroad with a flat
still in Ukraine. That means English articles must say they are about Ukraine —
see the recalculation article, whose first version presented Ukrainian rules as
universal and had to be corrected.

## Every article ends with a way to act

Each post now carries a call-to-action block before the "back to blog" link.
Before that the only link to the app on an article page was a text one in the
footer beside the privacy policy — the position nobody reads as an invitation.

⚠ The install link carries `&referrer=utm_source%3Dplatizhka.com.ua%26utm_medium%3Dblog`.
Play passes the referrer through to the install and reports tagged arrivals
apart from organic. Without it the entire content effort is unmeasurable: we
would never know whether a single install came from the site.

## When to look, and at what

Publishing weekly, a fifteen-page site earns meaningful search traffic in
**months, not weeks**. First measurement point: about eight weeks out.

Then read, in this order:
1. **GSC → Эффективность → Запросы** — which cluster produced impressions.
   That answers what to write more of.
2. **Play Console → acquisition, tracked channels** — whether the tagged link
   produced installs. That answers whether the site is worth the writing.
3. **Cloudflare Web Analytics** — pageviews and referrers, as context only.

⚠ Do not judge before that. Reading a two-week-old GSC report produces the
conclusion that nothing works, because nothing has had time to.
