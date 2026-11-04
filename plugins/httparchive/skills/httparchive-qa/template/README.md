# <Feature> QA: <candidate> vs <reference browsers> on pages that use it

<!-- Fill in or delete every comment and placeholder. Take each number from a committed file and
     say which. No billing project, account, job IDs, or costs; bytes processed only, in TiB. -->

<One or two sentences: what was tested, in which browsers and channels, on which pages.> Findings
are in [`findings/`](findings/), one directory per cause, each with a test case and per-browser
results. Filed issues have `[<owner>/<repo>]` at the end of their titles.

## Findings, ranked by impact

| # | Target | Issues | Finding |
|---|---|---|---|

## Findings in the infrastructure the feature builds on

<!-- Differences the feature-off control shares: engine behavior the feature relies on, and
     automation that behaves unlike a user. -->

| # | Target | Issues | Finding |
|---|---|---|---|

<!-- One paragraph: differences traced to the harness or to sites (UA sniffing, geo, bot blocks)
     rather than browsers. -->

## 1. Where the feature is used

<!-- Crawl date, tables, clients. Each query file, what it selects (use counters with where they
     fire), bytes processed, output file. Usage grouped by library, and how many pages act through
     the feature rather than only detecting it. -->

## 2. Live comparison

<!-- Scope as agreed at kickoff: setups (browser, channel, version, prefs/flags, controls),
     viewports, page sources and samples (seed, strata), interactions per visit, what's recorded,
     what's flagged, rechecks, stopping rule. Harness changes mid-run. -->

### Page results

<!-- Visits per setup, how often pages exercised the feature, pages flagged per setup, how many
     reproduced on recheck, and what the rest were. -->

## 3. Local tests

<!-- One bullet per test page: the pattern it covers (from pages' code or interop failures) and
     the result in each setup, or the finding it led to. -->

## Not covered

## Why the run stopped here

## Reproduce

```sh
```

<!-- Live pages change, so a rerun won't match exactly. Screenshots and page text aren't
     committed. -->
