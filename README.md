# web-platform-skills

Claude Code plugins for web platform spec and wpt work. Install either or both.

`web-platform-skills`:

- `wpt` skill: writing, running, and debugging web-platform-tests, and measuring browser behavior.
- `file-issue` skill: drafting spec issues and browser bugs, pre-filling Gecko/Chromium/WebKit/GitHub forms, and filling out WHATWG PR checklists.
- `browser-source` skill: finding and citing Gecko, Chromium, WebKit, and Ladybird code, with pinned permalinks, and checking engine behavior against the spec.
- `PreToolUse` hook: blocks `./wpt run ... firefox` on macOS while a Firefox update is staged, since the updater would hang on a password prompt.

`httparchive`:

- `httparchive` skill: querying HTTP Archive in BigQuery and estimating web compat impact, including checking estimates in a browser, with a template for a reproducible research repo. See [docs/httparchive.md](docs/httparchive.md) for how it works and where the data comes from.

The `httparchive` skill used to be part of `web-platform-skills`; install the `httparchive` plugin to keep it.

## Install

From Claude Code:

```
/plugin marketplace add zcorpan/web-platform-skills
/plugin install web-platform-skills@web-platform-skills
/plugin install httparchive@web-platform-skills
```

Or clone and symlink them into your skills directory, where they load as `web-platform-skills@skills-dir` and `httparchive@skills-dir`:

```
git clone https://github.com/zcorpan/web-platform-skills ~/git/zcorpan/web-platform-skills
ln -s ~/git/zcorpan/web-platform-skills ~/.claude/skills/web-platform-skills
ln -s ~/git/zcorpan/web-platform-skills/plugins/httparchive ~/.claude/skills/httparchive
```

## Prompting

Both styles work: a detailed prompt up front, or a short one that you steer as it goes. Claude
asks before anything billed or outward-facing (BigQuery queries, pushes, posts).

For a compat analysis with `httparchive`, a detailed prompt covers:

- The change, precisely: what behaves differently and which cases are affected.
- How to find affected pages: a use counter, custom metric, or string to search in
  `response_body`, with the crawl date, client, and root or all pages.
- The before/after switch: an engine flag or pref, a build to make or use, or how to emulate it.
- The browser to test in.
- Sample size and strata, and whether to also check all top-ranked hits.
- The budget: a per-query or total cap.
- What to deliver: research repo, summary, or a draft comment you review before posting.

A short prompt like "run httparchive analysis for &lt;issue>; there's no use counter, search
`response_body` for X" also works; expect to answer questions and correct course (scope, budget,
which browser) along the way.
