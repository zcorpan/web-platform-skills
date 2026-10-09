---
name: wpt
description: Use when writing, running, or debugging web-platform-tests (wpt), or when measuring how browsers actually behave (event and task ordering, timing, loading) with a throwaway test or by loading a page in Firefox, Chrome, or Safari. Triggers on "wpt", "web-platform-tests", "write a test", "./wpt run", "what do browsers do", "test this in Firefox/Chrome/Safari".
---

# wpt

## Running tests

- `./wpt run --no-pause --yes --binary "<path>" <product> <paths>` (`--yes` skips the webdriver prompt, `--no-pause` stops hanging).
- Local browsers on macOS: `/Applications/Firefox Nightly.app/Contents/MacOS/firefox` (`firefox`), `/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary` (`chrome`), `--webkit-port=safari safari` (Safari release), `--webkit-port=safari --channel preview safari` (Safari TP). Check the "Starting WebDriver:" line if unsure which channel ran.
- Re-run timing-sensitive results ~3 times before reporting them as stable.
- When many failures exist, baseline before attributing them to the change: `git stash`, run, `git stash pop`.
- Re-run with an added settle delay to rule out artifacts from the load event or queued tasks.

## Measuring browser behavior

- Write a throwaway test in a scratch dir and dump observations with `assert_true(false, '\n' + log.join('\n'))`. Record sync, microtask, task, rAF, and event handler timing in one run.
- Afterwards, delete the scratch dir and verify with `git status`.

## Driving a browser at an external URL

- Chrome: `chrome --headless --disable-gpu --virtual-time-budget=8000 --dump-dom "<url>"`.
- Firefox/Safari: raw W3C WebDriver over HTTP (POST `/session`, `/session/{id}/url`, `/session/{id}/execute/sync`, DELETE `/session/{id}`). geckodriver is at `_venv3/bin/geckodriver` in a bootstrapped wpt checkout. If safaridriver hangs, fall back to `./wpt run --channel preview` on a local equivalent.
- If browser MCP servers are configured, use them for interactive exploration only, and report results from `./wpt run`:
  - `safari-tp-mcp`: `create_tab`, `navigate_to_url`, `evaluate_javascript`, `browser_console_messages`, `screenshot`. `evaluate_javascript` takes a function body: use an explicit `return` or get `null`.
  - `chrome-canary-mcp` (isolated profile): `new_page`, `evaluate_script`, `list_console_messages`, `take_screenshot`. Every page tool needs `pageId` (from `new_page`/`list_pages`); `evaluate_script` takes a function (`() => ...`).
  - `firefox-nightly-mcp` (temp profile): `new_page`, `evaluate_script`, `screenshot_page`, `close_firefox_session`. `evaluate_script` takes a function (`() => ...`). No console tool by default.

## Writing tests

- Await events/callbacks (wrap in a promise) rather than polling. Poll with `await t.step_wait(() => video.currentSrc == source.src, 'desc', 3000, 5)` (adjust the 100ms default as needed) only for spec steps with no observable event, e.g. an algorithm resuming at a microtask checkpoint; don't sync those on a parse-time inline script (engines don't resume there).
- Prefer a sync point tied to the spec step over events (events are queued at a different step, and engines disagree on order).
- Sanity-check the sync point: assert the expected work is still pending, so the test fails loudly if the state is wrong.
- New `resources/` handler knobs: add an optional query param behind a presence check, so existing callers are unaffected.
- A test that fails identically in all browsers for an unrelated reason is worse than no test. Verify it would pass if the feature were implemented correctly.
- Give each media/image resource in a test a distinct URL (add a query string) so a cached copy can't make a lazy resource load eagerly.
- Don't listen for `load` on a parser-inserted iframe/img from a later script; it may already have fired. Await the window `load` event instead (such elements delay it).
- Don't rely on named access on the global (`iframe` for `id=iframe`); use `document.querySelector()`/`getElementById()`.
- Don't add code comments unless really necessary for understanding.
