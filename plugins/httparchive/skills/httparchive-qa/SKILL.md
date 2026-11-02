---
name: httparchive-qa
description: Use only when the user explicitly asks for an httparchive QA run, e.g. "httparchive qa for <feature>" or "httparchive-qa". It QAs an implementation (a browser's, a flag or pref, a new build, a polyfill or extension) against reference implementations on the real pages that use the feature, found with HTTP Archive or Common Crawl, reporting one fileable finding per cause. Queries are billed; get the user's confirmation before running any query that isn't a dry run.
---

# httparchive-qa

Read `../httparchive/SKILL.md` (relative to this skill's base directory) and follow its Common Crawl, Cost, Querying, Use counters, Custom metrics, Live comparison and Research repo sections. Its estimate sections don't apply: the output is bugs, not an extrapolated rate.

## Kickoff, while the user is there

- Find the feature's spec, which engines ship it, how to turn it off in the candidate (a pref or flag), and its known interop failures (wpt.fyi results for its tests in the browsers under test). Each failure is a lead to check against pages.
- Size usage cheaply before proposing a sample: use counters (read where they fire; uses that need interaction are missing from the crawl), the 10k sample tables, local Common Crawl. Group usage by the library or framework behind it, and separate pages that act through the feature from pages that only detect it or listen: bugs show up on the former.
- Start the repo (`/tmp/<feature>-qa/`) from `../httparchive/template/`, but fill in this skill's `template/README.md` instead of its README, and extend its one-browser before/after harness to the run's setups.
- Smoke-test automation in every setup on a local page that uses the feature, and run the first small query. List one-time actions only the user can do (enabling a driver, OS permissions, installing a runtime) and get them done now.
- Then propose the scope in one round of questions, with defaults:
  - Setups: the reference twice (noise floor), the candidate, the candidate with the feature off (separates the feature's bugs from other engine differences), and the other engines' current dev channels.
  - Pages: top-ranked pages that act through the feature first, plus some that only detect it (a candidate changes feature detection, so they take new code paths); the long tail and emulated mobile if they may use it differently.
  - Interactions that make pages exercise the feature, with user-like input rather than script where the feature can tell them apart.
  - The infrastructure the feature builds on: included by default, reported separately.
  - A budget for the whole run, approved once so it can run unattended; duration; stopping rule.
  - An effort level for the session: suggest `/effort xhigh` or `max` for a multi-hour unattended run.
- Record the agreed scope and stopping rule in the README, so a new context can resume the run.

## Running

- Work in batches. Rerun each flagged page twice in the reference, candidate and control before investigating; most flags are page noise.
- A difference is the feature's only if the control agrees with the reference. For an engine without a control, the feature-level trace (calls, events, results) must differ. A difference the control shares is in the underlying infrastructure, or a site difference.
- Instrument the feature with a preload trace in every setup and report how often pages actually exercised it. When pages rarely reach its active paths, shift effort to local test pages built from the patterns in the pages' code and the interop failures, run in every setup.
- Flag console errors and warnings only the candidate logs, not just exceptions (polyfills often log failures instead of throwing), and states only the candidate has (a loading indicator still up, raw content).
- For a polyfill or extension, read its code for where it differs from the reference by design (refetching, running in every frame, its own stylesheet, another realm) and write a test page per difference.
- Classify each cause: the candidate, another engine, the spec (its requirement breaks pages, or two or more implementations deviate from it the same way), the automation (a driver behaving unlike a user; report it with the infrastructure), or the site (UA sniffing, geo-targeting, bot blocks, consent flows). Rule out the last two before blaming an engine.
- Treat crashes as the most severe: a lost driver session can be a crashed content process. Reproduce in a fresh session and look for the stack in crash reports.
- Breadth over depth: once a cause has a reduced test, the engine code at a commit, and the spec step, tag later pages with the same signature and move on to new pages. Don't prototype or suggest fixes unless asked; then prototype before suggesting.
- Stop after two consecutive batches with no new cause, or when pages stop reaching new code paths, and record why in the README. Don't write a detailed follow-up plan; suggest a follow-up in rough shape only when there's reason to think it would find what this run missed.

## Findings

- One directory per cause: `findings/<NN>-<slug>/` for the feature, `findings/infra-<NN>-<slug>/` for the infrastructure, numbered by impact (severity × pages affected × rank). Each `finding.md` can be filed as is: target tracker and component; what's wrong, with engine code at a commit and the spec steps; the reduced test with per-browser results; affected pages "N of M"; and the search for existing reports. No fix suggestions.
- Commit the test pages, runner and output, plus the scans and a script that recomputes every count the findings cite; rerun it before publishing.
- Search the trackers and spec issues first. A known bug becomes a data point linked from the finding, not a new report.
- File only when asked, per the `file-issue` skill: one issue per finding, each title ending with `[<owner>/<repo>]` (or the user's tag). Then link every filed and existing issue from its finding and the README's tables.
