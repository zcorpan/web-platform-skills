# web-platform-skills

Claude Code plugins for web platform spec and wpt work. Install either or both.

`web-platform-skills`:

- `wpt` skill: writing, running, and debugging web-platform-tests, and measuring browser behavior.
- `file-issue` skill: drafting spec issues and browser bugs, pre-filling Gecko/Chromium/WebKit/GitHub forms, and filling out WHATWG PR checklists.
- `browser-source` skill: finding and citing Gecko, Chromium, WebKit, and Ladybird code, with pinned permalinks, and checking engine behavior against the spec.
- `PreToolUse` hook: blocks launching Firefox through WebDriver (`./wpt run ... firefox`, geckodriver, or a Python script using Selenium) on macOS while a Firefox update is staged, since the updater would hang on a password prompt.

`httparchive`:

- `httparchive` skill: querying HTTP Archive in BigQuery and estimating web compat impact, including checking estimates in a browser, or finding compat bugs in a polyfill or other implementation on the pages that use a feature, with a template for a reproducible research repo. See [docs/httparchive.md](docs/httparchive.md) for how it works and where the data comes from.

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
