---
name: file-issue
description: Use when drafting or filing a spec issue (WHATWG, W3C, or other GitHub-hosted specs) or a browser implementation bug (Chromium, WebKit, Mozilla Bugzilla), including pre-filling the new-issue form, or writing a WHATWG spec PR's description and checklist. Triggers on "file an issue", "spec issue", "file a bug", "report this to Chromium/WebKit/Gecko", "draft an issue", "open the PR", "edit the PR".
---

# file-issue

## Content

- One issue per issue; cut tangents. If a second problem appears, file it separately instead of adding a "Related" paragraph.
- Problem + evidence, then stop. One hedged sentence suggesting a fix is OK. Keep refs terse: "(Found in #123.)", not a clause.
- When suggesting a fix, verify its impact carefully to avoid regressions. Prefer the fix that changes the fewest implementations; don't resolve engine disagreement with implementation-defined or optional behavior.
- Quote the spec as a block quote (colon intro, "...and " continuation), not inline.
- Hedge implementation claims ("appear to run", "seems to") only when inferred from test results alone. If the engine source has also been read, state it with confidence ("runs"). Report observed behavior, not code.
- If the problem is spec-only and no browser distinguishes, omit browsers entirely. Don't report "couldn't reproduce".
- Never say "all engines" or "all three". Name the tested browsers/engines, pick one naming scheme, and state the channel. Say "Safari TP" when the tested browser was Safari Technology Preview; plain "Safari" means release.
- Issues containing an AI-drafted plan: open with a first-person paragraph (not `<details>`) saying it was drafted with Claude Code (model name), what was explored, and which decisions the user made; then put the whole plan in a block quote. Example: validator/validator#2143.

## Implementation bugs

- Title: for a spec change, the behavior change; for a defect, the observable symptom, not the cause or fix.
- Link a wpt test, or describe the repro and attach a test file.
- On non-GitHub trackers (Chromium, WebKit, Bugzilla), use full URLs, not `org/repo#N` shorthand.

## WHATWG PRs

- The description opens with the commit message. Backtick code there where needed, but not in git commit messages ([COMMITTING.md](https://github.com/whatwg/meta/blob/main/COMMITTING.md)). End it with `Tests: <wpt PR URL>.`, then `Fixes #N.`
- Implementer interest: list only Chromium, Gecko, and WebKit. An engine that already implements the behavior (its tests pass) counts as interested. Don't list other engines (e.g. Ladybird, Servo).
- Implementation bugs: link a bug for each of those engines that fails the tests, and mark the ones that pass as already matching. Don't write "N/A" until every engine passes. If an engine is known to diverge but the tests don't show it, improve the tests first.
- Skip the spec issue only for an obvious bug fix that implementations agree on; if they disagree, file an issue first.
- Renaming a `<dfn>`: keep the old anchor too. Removing one: point the old anchor at a note saying what was there and why it's gone. A removal needs a test that the feature is unsupported.

## Pre-filling forms

- Pre-fill the form so the user can review and edit before filing. Encode URL params with Python's `urllib.parse.urlencode`. Don't paste the URL or repeat the draft in chat.
- GitHub: `gh issue create --repo <org>/<repo> --web --title "..." --body-file <file>`. For YAML issue forms (`.github/ISSUE_TEMPLATE/*.yml`), open `/issues/new?template=<file>.yml&title=...&<field id>=...`; `body=` is ignored. If the field has no `id`, `pbcopy` the body and ask the user to paste it.
- Chromium: `https://issues.chromium.org/issues/new?noWizard=true&component=<id>&title=...&description=...`. The `<id>` for a component like `Blink>Image` is `buganizer_public.component_id` in its `DIR_METADATA`; in a Chromium checkout: `git grep -l 'component: "Blink>Image"' -- '*DIR_METADATA' | head -1 | xargs grep component_id`.
- Mozilla Bugzilla: `https://bugzilla.mozilla.org/enter_bug.cgi?product=Core&component=<component>&bug_type=enhancement&short_desc=...&comment=...` (`defect` if the spec didn't change), optionally with `see_also=<spec issue URL>` and `keywords=parity-chrome, parity-safari` (for missing features those browsers ship, to help prioritization; omit for minor bugs). Comments render Markdown. Find the component with `./mach file-info bugzilla-component <file>` in a Firefox checkout, else from similar bugs: `https://bugzilla.mozilla.org/rest/bug?quicksearch=<terms>&include_fields=id,summary,product,component`.
- WebKit: `https://bugs.webkit.org/enter_bug.cgi?product=WebKit&component=<component>&short_desc=...&comment=...`. No Markdown. Find the component from similar bugs: `https://bugs.webkit.org/rest/bug?quicksearch=<terms>&include_fields=id,summary,component`. The WAF blocks `<input`, `<iframe`, `<script`, `<body`, `<form`, `<svg`, `<textarea`, `<button`, `<object`, `<embed`, `<frame>`; `<a`, `<div`, `<p`, `<span`, `<math` pass.
