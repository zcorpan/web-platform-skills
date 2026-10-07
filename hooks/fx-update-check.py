#!/usr/bin/env python3
# PreToolUse hook: block `./wpt run ... firefox` while a Firefox update is
# staged. A fresh profile would otherwise spawn org.mozilla.updater, which
# needs authorization and hangs on a password prompt.
import json
import os
import re
import sys

command = json.load(sys.stdin).get("tool_input", {}).get("command", "")
if not re.search(r"\bwpt run\b", command) or "firefox" not in command:
    sys.exit(0)

app = re.search(r"/Applications/([^/]+)\.app", command)
app_name = app.group(1) if app else "Firefox Nightly"
status = os.path.expanduser(
    f"~/Library/Caches/Mozilla/updates/Applications/{app_name}/updates/0/update.status"
)
if os.path.exists(status):
    print(
        f"{app_name} has a staged update ({status} exists). Ask the user to restart "
        f"{app_name}, and don't run wpt until that file is gone.",
        file=sys.stderr,
    )
    sys.exit(2)
