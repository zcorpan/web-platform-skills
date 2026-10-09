---
name: httparchive
description: Use when measuring how the web uses a feature, or estimating the web compat impact of a spec or browser change, with HTTP Archive data in BigQuery, including checking crawl-based estimates by loading sampled pages in a browser. Triggers on "HTTP Archive", "httparchive", "research compat impact", "research how many pages use", "research whether this is web compatible". Queries are billed; get the user's confirmation before running any query that isn't a dry run.
---

# httparchive

## Cost

- Queries bill the user's Google Cloud project. Before the first query that isn't a dry run, show the dry-run estimate and wait for explicit approval, even if the user asked for HTTP Archive data and especially if this skill loaded on its own. Ask again for any query above a budget or per-query cap the user approved.
- Dry-run every query (`--dry_run`) and always pass `--maximum_bytes_billed`.
- Cost depends on the columns read, not the rows returned: `LIMIT` doesn't reduce it, `TABLESAMPLE SYSTEM (n PERCENT)` does. Reading one `custom_metrics` sub-field over all root pages costs far less than reading `payload` or the `requests` table.
- The dry-run number is an upper bound: sampling and filters on clustered columns (e.g. `client`) cut the bytes billed but not the estimate.
- Prototype on a sample, then run the full query once. 1% is fine for small columns; for very large ones (e.g. `response_body` in the `requests` table), start at `TABLESAMPLE SYSTEM (0.1 PERCENT)`.
- Get actual cost from job stats (`bq ls -j --format=json`, `statistics.query.totalBytesBilled`). `-a` includes other users' jobs, so filter on `user_email`.

## Querying

- Docs: https://har.fyi/. Pass SQL on stdin (`bq query --use_legacy_sql=false < q.sql`); a leading `--` comment in an argument is parsed as a flag.
- `TABLESAMPLE` gives a different sample each run. For a reproducible sample, order by `FARM_FINGERPRINT(CONCAT(page, '<seed>'))` and take the first N, per stratum with `ROW_NUMBER() OVER (PARTITION BY ...)`.
- A sampled table can't be referenced twice in one query; get totals with `GROUP BY ROLLUP(...)` instead of a `UNION`.
- `STRING()`, `BOOL()`, etc. throw on a value of the wrong type, and a full-table run can hit values a sample didn't. Use `LAX_STRING()`, `LAX_BOOL()`, `SAFE.INT64()`. Quote hyphenated JSON keys: `'$."responsive-images"'`.

## Custom metrics

- Read the metric's source (HTTPArchive/custom-metrics, `dist/<name>.js`) before using a field: what it measures, when (in Chrome, after load, at the crawl's viewport), and how derived fields are computed.
- Derived fields can share an input (e.g. an "error" computed from the metric's own parse of an attribute), so two conditions that look independent can be one signal. Prefer fields read straight from the DOM.
- Metric parsers lag the spec (new keywords, syntax). Check parse-error fields, and exclude or count those cases separately.
- Look at ~20 flagged examples before trusting a count: hidden elements (`clientWidth` 0), min/max clamping, pages that changed since the crawl.

## Estimating compat impact

- State the denominator: crawl date, client, root pages only (`is_root_page`) or all pages, and "pages with at least one X" vs all pages.
- Where crawl data can't decide, use separate "definitely changes" and "might change" buckets rather than guessing.
- Check the estimate on a seeded, stratified random sample (~100 per bucket) loaded live in a browser that matches the crawl (Chrome; the mobile client's viewport is 360px wide).
- Emulate the proposed behavior on a current engine by rewriting the page so the old algorithm produces the new result, instead of waiting for an implementation.
- Measure before twice (A, then A2 a few seconds later) and after (B). Differences between A and A2 are page noise (carousels, animations, ads). Record element boxes and scroll size, and take full-page screenshots at CSS-pixel scale.
- Review changed pages by eye, cropped around the changed element. Rate each one broken, worse, neutral, improved, no visible change, or not assessable (consent dialog, blank page). A changed layout isn't breakage, and improvements don't offset breakage.
- Extrapolate per stratum, (hits / sample size) × stratum size, summed. With only 1 or 2 hits, give exact binomial intervals with the estimate.
- For batch runs, use Playwright in a venv with a few pages in parallel; append one JSON line per page and skip pages already done, so the run can resume.
