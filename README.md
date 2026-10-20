# web-platform-skills

A Claude Code plugin for web platform spec and wpt work.

- `wpt` skill: writing, running, and debugging web-platform-tests, and measuring browser behavior.
- `file-issue` skill: drafting spec issues and browser bugs, and pre-filling Chromium/WebKit/GitHub forms.
- `browser-source` skill: finding and citing Gecko, Chromium, WebKit, and Ladybird code, with pinned permalinks, and checking engine behavior against the spec.
- `httparchive` skill: querying HTTP Archive in BigQuery and estimating web compat impact, including checking estimates in a browser, with a template for a reproducible research repo.
- `PreToolUse` hook: blocks `./wpt run ... firefox` on macOS while a Firefox update is staged, since the updater would hang on a password prompt.

## Install

From Claude Code:

```
/plugin marketplace add zcorpan/web-platform-skills
/plugin install web-platform-skills@web-platform-skills
```

Or clone and symlink it into your skills directory, where it loads as `web-platform-skills@skills-dir`:

```
git clone https://github.com/zcorpan/web-platform-skills ~/git/zcorpan/web-platform-skills
ln -s ~/git/zcorpan/web-platform-skills ~/.claude/skills/web-platform-skills
```

## Prompting

Both styles work: a detailed prompt up front, or a short one that you steer as it goes. Claude
asks before anything billed or outward-facing (BigQuery queries, pushes, posts).

For a compat analysis with `httparchive`, a detailed prompt covers:

- The change, precisely: what behaves differently and which cases are affected.
- How to find affected pages: a use counter, custom metric, or string to search in
  `response_body`, with the crawl date, client, and root or all pages.
- The before/after switch: an engine flag or pref, a build to make or use, or how to emulate it.
- The browser that matches the change (Chrome for Blink, Firefox for Gecko).
- Sample size and strata, and whether to also check all top-ranked hits.
- The budget: a per-query or total cap.
- What to deliver: research repo, summary, or a draft comment you review before posting.

A short prompt like "run httparchive analysis for <issue>; there's no use counter, search
`response_body` for X" also works; expect to answer questions and correct course (scope, budget,
which browser) along the way.
