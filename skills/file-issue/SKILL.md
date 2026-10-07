---
name: file-issue
description: Use when drafting or filing a spec issue (WHATWG, W3C, or other GitHub-hosted specs) or a browser implementation bug (Chromium, WebKit, Mozilla Bugzilla), including pre-filling the new-issue form. Triggers on "file an issue", "spec issue", "file a bug", "report this to Chromium/WebKit/Gecko", "draft an issue".
---

# file-issue

## Content

- One issue per issue; cut tangents. If a second problem appears, file it separately instead of adding a "Related" paragraph.
- Problem + evidence, then stop. One hedged sentence suggesting a fix is OK. Keep refs terse: "(Found in #123.)", not a clause.
- When suggesting a fix, verify its impact carefully to avoid regressions.
- Quote the spec as a block quote (colon intro, "...and " continuation), not inline.
- Hedge implementation claims ("appear to run", "seems to") only when inferred from test results alone. If the engine source has also been read, state it with confidence ("runs"). Report observed behavior, not code.
- If the problem is spec-only and no browser distinguishes, omit browsers entirely. Don't report "couldn't reproduce".
- Never say "all engines" or "all three". Name the tested browsers/engines, pick one naming scheme, and state the channel. Say "Safari TP" when the tested browser was Safari Technology Preview; plain "Safari" means release.
- Issues containing an AI-drafted plan: open with a first-person paragraph (not `<details>`) saying it was drafted with Claude Code (model name), what was explored, and which decisions the user made; then put the whole plan in a block quote. Example: validator/validator#2143.

## Implementation bugs

- Link a wpt test, or describe the repro and attach a test file.
- On non-GitHub trackers (Chromium, WebKit, Bugzilla), use full URLs, not `org/repo#N` shorthand.

## Pre-filling forms

- GitHub: `gh issue create --repo <org>/<repo> --web --title "..." --body-file <file>`. For YAML issue forms, use `?title=`/`?body=` URL params instead; check `.github/ISSUE_TEMPLATE/*.yml` for field ids.
- Chromium: `https://issues.chromium.org/issues/new?noWizard=true`.
- Mozilla Bugzilla: `https://bugzilla.mozilla.org/enter_bug.cgi?product=Core&component=<component>&bug_type=defect&short_desc=...&comment=...`, optionally with `see_also=<spec issue URL>` and `keywords=parity-chrome, parity-safari` (for missing features those browsers ship, to help prioritization; omit for minor bugs). Comments render Markdown. Find the component from similar bugs: `https://bugzilla.mozilla.org/rest/bug?quicksearch=<terms>&include_fields=id,summary,product,component`.
- WebKit: `https://bugs.webkit.org/enter_bug.cgi?product=WebKit&component=<component>&short_desc=...&comment=...`. No Markdown. The WAF blocks `<input`, `<iframe`, `<script`, `<body`, `<form`, `<svg`, `<textarea`, `<button`, `<object`, `<embed`, `<frame>`; `<a`, `<div`, `<p`, `<span`, `<math` pass.
