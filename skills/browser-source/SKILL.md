---
name: browser-source
description: Use when finding or citing the code in Gecko, Chromium, WebKit, or Ladybird that implements some web platform behavior, e.g. to explain a measured browser difference, check whether an engine matches a spec step, or link engine code in a spec issue or bug. Triggers on "find the code in Gecko/Chromium/WebKit", "where does Firefox/Chrome/Safari do X", "why does this browser do X", "searchfox", "Chromium Code Search".
---

# browser-source

## Finding code

- Start from the spec: engines cite spec URLs in comments (Ladybird nearly always), so grep for the section's anchor. For Gecko, `searchfox-cli --spec-refs '<url>'` (see the `webspec-index` skill).
- Prefer a local checkout and `git grep`; otherwise Searchfox (Gecko), Chromium Code Search, and GitHub (WebKit, Ladybird).
- For several engines, run one subagent per engine in parallel. Give each the scenario and the measured result, and ask for the first check that fires, short excerpts, and pinned permalinks.
- Read at a commit (`git show <sha>:<path>`), not the working tree; local edits and sparse checkouts shift or hide lines.

## Citing code

- Pin links to a commit:
  - Gecko: `https://github.com/mozilla-firefox/firefox/blob/<sha>/<path>#L<a>-L<b>`
  - Chromium: `https://source.chromium.org/chromium/chromium/src/+/<sha>:<path>;l=<n>`
  - WebKit: `https://github.com/WebKit/WebKit/blob/<sha>/<path>#L<a>-L<b>`
  - Ladybird: `https://github.com/LadybirdBrowser/ladybird/blob/<sha>/<path>#L<n>`
- Re-read every cited line at that commit yourself before using a subagent's citation.
- Separate the check that fires in the scenario from backstops that only matter in other cases, and say which is which.
- In prose, name the function and link it; describe what the check does instead of pasting code.
- State what was read in source plainly. Hedge what was inferred, such as a path traced by reading but not run.

## Comparing with the spec

- Before calling an engine divergent, check whether the spec leaves the step to the user agent ("may", "intends to", "implementation-defined"). If it does, the engine conforms, and the issue is the spec path a conforming UA can still reach.
