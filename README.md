# web-platform-skills

Claude Code plugins for web platform spec and wpt work. Install either or both.

`web-platform-skills`:

- `wpt` skill: writing, running, and debugging web-platform-tests, and measuring browser behavior.
- `file-issue` skill: drafting spec issues and browser bugs, pre-filling Gecko/Chromium/WebKit/GitHub forms, and filling out WHATWG PR checklists.
- `browser-source` skill: finding and citing Gecko, Chromium, WebKit, and Ladybird code, with pinned permalinks, and checking engine behavior against the spec.
- `PreToolUse` hook: blocks launching Firefox through WebDriver (`./wpt run ... firefox`, geckodriver, or a Python script using Selenium) on macOS while a Firefox update is staged, since the updater would hang on a password prompt.

`httparchive`:

- `httparchive` skill: measuring how the web uses a feature and estimating web compat impact with HTTP Archive (BigQuery) and Common Crawl, and checking estimates in a browser, with a template for a reproducible research repo.
- `httparchive-qa` skill: QA runs of an implementation (a browser's, a flag or pref, a build, a polyfill or extension) against other implementations on the pages that use the feature, with one fileable finding per cause. It loads only when asked for by name ("httparchive qa for &lt;feature>").
- `page-reviewer` agent: a read-only reviewer (no shell or network) that both skills hand crawl and page material to, so instructions planted in pages can't run commands through it.

See [docs/httparchive.md](docs/httparchive.md) for how they work and where the data comes from.

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
