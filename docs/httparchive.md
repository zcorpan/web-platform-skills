# Web compat research with the `httparchive` skill

The `httparchive` skill helps Claude answer "is this spec or browser change web compatible?" It
finds pages the change would affect in public crawl data, loads a sample of them in a real browser
with and without the change, reviews the differences, and writes it all up in a reproducible git
repo you can publish.

## Where the data comes from

**Chrome UX Report (CrUX).** Chrome users who opt in to usage statistics reporting and sync their
history send anonymized data about the sites they visit, and Google publishes it monthly as
[CrUX](https://developer.chrome.com/docs/crux/methodology). A site is included only if it's
publicly discoverable (indexable, as for search engines) and has enough visitors. CrUX also gives
each site a coarse popularity rank: top 1k, 10k, 100k, 1M, and so on. Intranets, logged-in-only
pages, Chrome on iOS, and other Chromium browsers aren't in it.

**HTTP Archive.** Each month, [HTTP Archive](https://httparchive.org/) takes the CrUX site list
(in the 2026-10-01 crawl, 15.4 million sites on mobile and 11.7 million on desktop) and loads each
site's home page (the "root page") and one additional page linked from it in Chrome: once as
desktop, once as emulated mobile. It loads them from US datacenters, logged out, with an empty
cache, and doesn't click or type anything. For each page it stores the responses (HTML, scripts,
CSS), which Chrome use counters fired, the output of custom metrics (scripts run on the page after
load), and more. It's all in a public BigQuery dataset; see [har.fyi](https://har.fyi/) and the
Web Almanac's [methodology](https://almanac.httparchive.org/en/2025/methodology).

**Use counters.** Browsers count how often features are used. A use counter is a line of engine
code that fires when a code path runs; Chrome publishes each counter's rate as "% of page loads" on
[chromestatus](https://chromestatus.com/metrics/feature/popularity). When a counter matches the
change, HTTP Archive lists which crawled pages hit it, which is the cheapest way to find affected
pages. Firefox has its own counters too.

**Common Crawl.** [Common Crawl](https://commoncrawl.org/) is a nonprofit that crawls billions of
URLs (not only home pages) and publishes the raw responses as WARC files anyone can download, free
and without an account. It has no popularity ranks or use counters, only the responses. The skill
uses a random sample of WARCs (12 files, about 12 GB and 250k pages) to try out searches for free
before spending money on HTTP Archive.

## How a research run goes

1. You describe the change and, if you know, how to find affected pages: a use counter, or a
   pattern in markup, CSS or scripts (see Prompting below).
2. Claude finds candidate pages: by use counter in HTTP Archive, or for patterns by scanning
   Common Crawl first and then running one HTTP Archive query for counts and popularity ranks.
3. Before any billed query, Claude does a dry run, shows you how much data it would read, and waits
   for your OK.
4. It loads the pages live: today's behavior twice (to see what changes on its own, like ads and
   carousels) and with the change once. The change comes from a browser flag or pref, a build you
   provide, or by rewriting the page. It records JS errors, layout, and full-page screenshots.
5. Pages that differ are reviewed by eye and rated broken, worse, no visible change, improved, and
   so on. If the change only alters what scripts see, it can also trace what scripts do with the
   changed results.
6. It extrapolates from the sample to the whole crawl, per popularity bucket.
7. Everything goes in a git repo made from the skill's template: queries, results, scripts, review
   images, and a README. A pre-commit hook checks that nothing that identifies you (your IP or
   location, which live pages can show) gets committed.
8. Claude drafts a comment for the spec issue or bug. When you're happy with it, it gives you the
   commands to create the GitHub repo and post the comment, and you run them.

## Finding bugs in an implementation

The same setup can test an implementation instead of a change: a polyfill or browser extension
against native support, a flag or pref, a new build, or one browser against another. Claude loads
the pages that use the feature (often the pages from an earlier compat run) with the reference and
with the candidate, flags differences and errors only the candidate shows, reduces each cause to a
minimal test page, and drafts one issue per cause for the candidate's tracker.

## Prompting

Both styles work: a detailed prompt up front, or a short one that you steer as it goes. Claude
asks before anything billed or outward-facing (BigQuery queries, pushes, posts).

A detailed prompt covers:

- The change, precisely: what behaves differently and which cases are affected.
- How to find affected pages: a use counter, a custom metric, or a pattern to search for in
  markup, CSS or scripts.
- How to turn the change on and off, and in which browser: a flag or pref, a build to make or use,
  or how to emulate it.
- The budget: a per-query or total cap.

Claude picks defaults for the rest (crawl date, desktop or mobile, sample size); mention them only
if you have a preference.

A short prompt like "run httparchive analysis for &lt;issue>; there's no use counter, search
response bodies for X" also works. Claude works out the rest from the issue and keeps going until it
needs you, such as to approve the first billed query or to provide a browser build. Correct course
along the way if its choices don't match what you want.

## Examples

Research made with the skill:

| Question | How |
|---|---|
| Can `<form name=createElement>` and similar stop shadowing `document`'s methods and other inherited properties, not just its attributes? | Found pages via a Chrome use counter, then compared Firefox Nightly with its pref off and on.<br>[Repo](https://github.com/zcorpan/document-shadowing-compat-10687), [comment](https://github.com/whatwg/html/issues/10687#issuecomment-6492266222). |
| Can the HTML parser treat `<noscript>` the same in every document, based only on whether JavaScript is enabled? | Chrome use counters, random and top-ranked samples, and a patched Firefox build that switches between the behaviors.<br>[Repo](https://github.com/zcorpan/noscript-compat-10879), [comment](https://github.com/whatwg/html/issues/10879#issuecomment-6440928253). |
| Can `style`, `script`, `title` and similar parse the same inside SVG/MathML as in HTML, to prevent a class of XSS? | Compared several parser variants, using a patched html5lib and a Firefox build.<br>[Repo](https://github.com/zcorpan/foreign-rawtext-compat-11397), [comment](https://github.com/whatwg/html/issues/11397#issuecomment-6454458598). |
| What breaks if browsers remove XSLT? | Use counters, plus Chrome with XSLT on and off.<br>[Repo](https://github.com/zcorpan/xslt-compat-11523), [comment](https://github.com/whatwg/html/issues/11523#issuecomment-6263966715). |
| Do the XSLT polyfill extensions render those pages like native XSLT? | Ran the same pages in Chrome and Firefox with native XSLT, and with it off and the extension installed; filed the polyfill and extension bugs found.<br>[Repo](https://github.com/zcorpan/xslt-compat-11523#5-xslt-polyfill-extensions), [comment](https://github.com/whatwg/html/issues/11523#issuecomment-6540232318). |
| What changes if an image chosen by `srcset` `w` descriptors always gets `sizes` as its natural width, even when `w` doesn't match the file's real width? | Started from an HTTP Archive custom metric, then emulated the new rule in Chrome.<br>[Repo](https://github.com/zcorpan/sizes-compat-3981), [comment](https://github.com/whatwg/html/issues/3981#issuecomment-6055848216). |
| Can Firefox remove the nonstandard IndexedDB `mozGetAll`? | Searched response bodies for the name, separated real code from minifiers' name lists, and tested a Firefox build with it removed.<br>[Repo](https://github.com/zcorpan/mozgetall-compat-1577227), [comment](https://bugzilla.mozilla.org/show_bug.cgi?id=1577227#c11). |

## What you need

- Claude Code with this plugin (see [Install](../README.md#install)).
- For HTTP Archive: a Google Cloud project with billing enabled, and the
  [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) (`gcloud auth login`; it includes
  `bq`). BigQuery bills by data read, not rows returned: on demand, $6.25 per TiB at the time of
  writing, with the first TiB each month free
  ([pricing](https://cloud.google.com/bigquery/pricing)). Use counters for all root pages in one
  crawl are about 0.1 TiB (under $1); searching every response body in one crawl is about 200 TiB
  (over $1,000), which is why the skill tries searches on Common Crawl and HTTP Archive's 10k-page
  sample tables first. Tell Claude your budget; it caps every query and shows the size and cost
  before running it.
- Python 3. Claude sets up a virtual environment for the scripts.
- The browsers to test in, such as Chrome Canary or Firefox Nightly, or your own engine build with
  the change. The scripts drive them with Playwright (Chromium) or Selenium (Firefox), installed in
  the virtual environment; no browser MCP server is needed.
- Optionally, disk space for Common Crawl WARCs (about 1 GB each).

## Limits

- The crawl is mostly home pages. Deep links, feeds, logged-in apps, and intranets are missing or
  underrepresented. Chrome's field rates include them, so a field rate much higher than the crawl's
  may mean the crawl undercounts, or that the feature is on a few heavily used pages (field rates
  count page loads, not pages).
- Pages are only loaded. Breakage that needs clicks, typing, or form submission isn't seen unless
  you ask for it to be tested.
- Live pages change after they're crawled, and they can differ by country.
- Results come from a sample: 0 broken out of 150 doesn't mean 0 on the web.
- Claude makes mistakes. Look at the repo and the review images before relying on the conclusion.
