# web-platform-skills

A Claude Code plugin for web platform spec and wpt work.

- `wpt` skill: writing, running, and debugging web-platform-tests, and measuring browser behavior.
- `file-issue` skill: drafting spec issues and browser bugs, and pre-filling Chromium/WebKit/GitHub forms.
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
