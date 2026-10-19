---
name: httparchive
description: Use when measuring how the web uses a feature, or estimating the web compat impact of a spec or browser change, with HTTP Archive data in BigQuery, including checking crawl-based estimates by loading sampled pages in a browser. Triggers on "HTTP Archive", "httparchive", "research compat impact", "research how many pages use", "research whether this is web compatible". Queries are billed; get the user's confirmation before running any query that isn't a dry run.
---

# httparchive

## Cost

- Queries bill the user's Google Cloud project. Before the first query that isn't a dry run, show the dry-run estimate and wait for explicit approval, even if the user asked for HTTP Archive data and especially if this skill loaded on its own. Ask again for any query above a budget or per-query cap the user approved.
- Dry-run every query (`--dry_run`) and always pass `--maximum_bytes_billed`.
- Cost depends on the columns read, not the rows returned: `LIMIT` doesn't reduce it, `TABLESAMPLE SYSTEM (n PERCENT)` does. Reading one `custom_metrics` sub-field over all root pages costs far less than reading `payload` or the `requests` table (~200 TB per crawl date in 2026).
- The dry-run number is an upper bound, and `--maximum_bytes_billed` is checked against it before the query starts. `TABLESAMPLE` and filters on later clustering columns (`type`, `rank`) don't lower it, so a sampled or filtered query is rejected unless the cap covers the full estimate; a `client` filter does lower it. A `type` filter didn't lower bytes billed for `response_body` either.
- Prototype on a sample, then run the full query once. 1% is fine for small columns. For `response_body`, prototype on `httparchive.sample_data.requests_10k` (also `pages_10k`, `parsed_css_10k`: ~10k root pages per client, recent crawls); a sampled `crawl.requests` query needs a cap at or above the full estimate, which then doesn't protect anything, so get approval for that cap.
- Get actual cost from job stats (`bq ls -j --format=json`, `statistics.query.totalBytesBilled`). `-a` includes other users' jobs, so filter on `user_email`.

## Querying

- Setup: `bq` comes with the Google Cloud CLI (`brew install --cask gcloud-cli` on macOS); `gcloud auth login`, then set a default project to bill.
- Docs: https://har.fyi/. Pass SQL on stdin (`bq query --use_legacy_sql=false < q.sql`); a leading `--` comment in an argument is parsed as a flag.
- `TABLESAMPLE` gives a different sample each run. For a reproducible sample, order by `FARM_FINGERPRINT(CONCAT(page, '<seed>'))` and take the first N, per stratum with `ROW_NUMBER() OVER (PARTITION BY ...)`.
- Substring hits in `response_body` are often name lists (minifiers' and obfuscators' reserved DOM names, e.g. terser's `domprops`; fingerprinting lists). Return `FARM_FINGERPRINT(response_body)` and regex snippets around the match, classify each distinct body, and fetch live copies (untrusted) when snippets aren't enough. Don't drop list hits unread: a listed name can still be looked up or called, so check them in a browser.
- A sampled table can't be referenced twice in one query; get totals with `GROUP BY ROLLUP(...)` instead of a `UNION`.
- `STRING()`, `BOOL()`, etc. throw on a value of the wrong type, and a full-table run can hit values a sample didn't. Use `LAX_STRING()`, `LAX_BOOL()`, `SAFE.INT64()`. Quote hyphenated JSON keys: `'$."responsive-images"'`.

## Use counters

- Look for an existing use counter before writing a query: Chromium `third_party/blink/public/mojom/use_counter/metrics/web_feature.mojom` (and `css_property_id.mojom`), Gecko `dom/base/UseCounters.conf`.
- Read where the counter is incremented before trusting it. It may fire on feature detection or on cases the change doesn't affect, or miss cases it does; counters for the same feature can differ by orders of magnitude.
- Chrome rates (% of page loads) are on chromestatus: `https://chromestatus.com/metrics/feature/timeline/popularity/<id>`, JSON at `https://chromestatus.com/data/timeline/featurepopularity?bucket_id=<id>`. Daily values are noisy and seasonal; look at months, not a day. Gecko rates are the `use.counter.*` Glean metrics in GLAM.
- Field rates include pages the crawl misses (logged-in, intranet, deep links). A field rate far above the crawl rate means the crawl undercounts; say so with the estimate.
- `pages.features` lists the Blink use counters each page hit during the crawl (`feature`, `id`, `type`: `default` or `css`). When a counter matches the change, use it to find the pages to review: `EXISTS(SELECT 1 FROM UNNEST(features) WHERE id = '<id>' AND type = 'default')`. Crawls from before the counter landed in Chrome stable don't have it. The crawl only loads each page, so counters that need user interaction (clicks, typing, form submission, navigation) or happen late won't be in it; there, an empty or low crawl count isn't evidence of low usage.
- Once a removal or behavior change reaches Chrome stable, later crawls run with it, and counters that only fire when the old behavior runs go quiet. Use crawls from before it shipped.

## Custom metrics

- Read the metric's source (HTTPArchive/custom-metrics, `dist/<name>.js`) before using a field: what it measures, when (in Chrome, after load, at the crawl's viewport), and how derived fields are computed.
- Derived fields can share an input (e.g. an "error" computed from the metric's own parse of an attribute), so two conditions that look independent can be one signal. Prefer fields read straight from the DOM.
- Metric parsers lag the spec (new keywords, syntax). Check parse-error fields, and exclude or count those cases separately.
- Look at ~20 flagged examples before trusting a count: hidden elements (`clientWidth` 0), min/max clamping, pages that changed since the crawl.

## Estimating compat impact

- State the denominator: crawl date, client, root pages only (`is_root_page`) or all pages, and "pages with at least one X" vs all pages.
- Stop early when partial data already shows the change isn't web compatible (e.g. a sample query or the first reviewed pages show breakage at a level that rules out shipping): say so, and ask whether to write up the data so far or continue. Concluding that a change is compatible needs the full check.
- The crawl visits root pages plus one linked page per site, so resources mostly reached by direct URL (feeds, sitemaps, API endpoints, standalone documents) are underrepresented. If usage concentrates there, say the crawl can't size it and look for other evidence.
- Where crawl data can't decide, use separate "definitely changes" and "might change" buckets rather than guessing.
- Check the estimate on a seeded, stratified random sample (~100 per bucket) loaded live in a browser that matches the crawl (Chrome; the mobile client's viewport is 360px wide).
- Before emulating, look for an existing switch: Chromium runtime features (`--disable-blink-features=<Name>`, `--enable-blink-features=<Name>`, from `runtime_enabled_features.json5`) or `--disable-features=<Name>`, Firefox prefs (`StaticPrefList.yaml`). Check that it takes effect in the build you use.
- Otherwise, emulate the proposed behavior on a current engine by rewriting the page so the old algorithm produces the new result. If that's impossible or only approximate (e.g. timing, parsing, or loading changes), ask the user for a browser build that implements the change, and compare it against an unmodified build of the same version.
- For a Gecko change, test in Firefox. Playwright's Firefox is a patched build that can't drive a local build; use Selenium with geckodriver and `enable_bidi` (JS errors via `script.add_javascript_error_handler`, console via `add_console_message_handler`, preload scripts via `script.pin`). Exclude CSP reports when comparing errors; they carry random tracking URLs.
- To emulate removing a WebIDL member in Gecko, add `Pref="..."` to it plus a `StaticPrefList.yaml` entry (`RelaxedAtomicBool`, `mirror: always`, so workers can read it), and build in a git worktree with its own objdir. Extension content scripts can't emulate it: they don't run in workers.
- Gecko use counters work as a detection pass: with `dom.use_counters.dump.{document,page,worker}` set, Firefox prints `USE_COUNTER_<KIND>: <metric> - <url>` to stderr when the document is destroyed. Open each page in a new tab, close it, then read the new lines in the browser's stderr (geckodriver's `log_output`). Dedicated workers' deprecated-operation counters land on the ancestor document; shared and service workers have none. Run detection over every hit, then compare before and after on the pages that hit. Counters only fire on calls; to also catch feature detection, a preload script can swap the member for a logging accessor (main thread only).
- Measure before twice (A, then A2 a few seconds later) and after (B). Differences between A and A2 are page noise (carousels, animations, ads). Record element boxes and scroll size, and take full-page screenshots at CSS-pixel scale.
- Review changed pages by eye, cropped around the changed element (the whole page when the whole document changes). Rate each one broken, worse, neutral, improved, no visible change, or not assessable (consent dialog, blank page). Rate against what the page is for: a machine-readable resource (feed, sitemap, API) losing its human-facing presentation is worse, not broken. A changed layout isn't breakage, and improvements don't offset breakage.
- Extrapolate per stratum, (hits / sample size) × stratum size, summed. With only 1 or 2 hits, give exact binomial intervals with the estimate.
- If the sample has few or no top-ranked pages (`rank`), run every top-ranked hit through the same steps and report them separately.
- For batch runs, use Playwright in a venv with a few pages in parallel; append one JSON line per page and skip pages already done, so the run can resume. Wrap each page visit in an overall timeout (e.g. `asyncio.wait_for`) and record a timeout as an error: `page.evaluate` and `context.close` have no timeout of their own, so one hung page holds a slot forever and stalls the run.

## Research repo

- For compat research, build a reproducible repo as you go: copy `template/` from this skill's directory to `/tmp/<feature>-compat-<issue>/` and `git init` it. Keep queries, their output, sample, scripts, logs, and review images there, so it can be moved and pushed as is. Create or push a GitHub repo only when asked.
- The template implements the batch-run rules above for Chromium; for Firefox, rewrite `harness.py` with Selenium as described above. Put the change in `change.py` (before/after setup, sanity check, extra measurements, change-specific auto-ratings); `harness.py`, `compare.py`, `analyze.py`, `recheck.py`, `sample.py`, and `extrapolate.py` are generic. Adapt them when the change needs it, and commit the versions that produced the data; if a script changed mid-run, say so in the README.
- Fill in `README.md` from the template's structure. Take every number from a committed file, and before publishing rerun `analyze.py` and `extrapolate.py` on the committed data and recount the README's numbers from the files.
- Leave out billing project, account, job IDs, and costs; give bytes processed per query. Screenshots stay out (`.gitignore`); commit the review images that ratings rely on.
