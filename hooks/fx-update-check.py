#!/usr/bin/env python3
# PreToolUse hook: block commands that launch Firefox through WebDriver
# (`./wpt run ... firefox`, geckodriver, or a Python script using Selenium)
# while a Firefox update is staged. A fresh profile would otherwise spawn
# org.mozilla.updater, which needs authorization and hangs on a password prompt.
import glob
import json
import os
import re
import shlex
import sys

UPDATES = os.path.expanduser("~/Library/Caches/Mozilla/updates/Applications")

hook_input = json.load(sys.stdin)
command = hook_input.get("tool_input", {}).get("command", "")
cwd = hook_input.get("cwd") or os.getcwd()


def python_sources():
    """Yield inline `python -c` code and Python scripts in the command, with
    the modules they import from their own directory."""
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    pending = []
    for i, token in enumerate(tokens):
        if token == "-c" and i > 0 and "python" in tokens[i - 1] and i + 1 < len(tokens):
            pending.append((tokens[i + 1], cwd))
        elif token.endswith(".py"):
            pending.append((None, os.path.join(cwd, os.path.expanduser(token))))
    seen = set()
    while pending:
        source, path = pending.pop()
        if source is None:
            path = os.path.realpath(path)
            if path in seen:
                continue
            seen.add(path)
            try:
                with open(path, encoding="utf-8", errors="replace") as f:
                    source = f.read()
            except OSError:
                continue
            path = os.path.dirname(path)
        yield source
        for names in re.findall(r"^[ \t]*(?:from[ \t]+(\w+)|import[ \t]+([\w \t,]+))", source, re.M):
            for name in re.split(r"[ \t,]+", " ".join(names)):
                if name:
                    pending.append((None, os.path.join(path, name + ".py")))


def launches_firefox():
    if re.search(r"\bwpt run\b", command) and "firefox" in command:
        return True
    if re.search(r"(?:^|[;&|(]\s*)(?:\S*/)?geckodriver\b", command):
        return True
    return any(
        re.search(r"\bselenium\b", source) and re.search(r"firefox", source, re.I)
        for source in python_sources()
    )


if not launches_firefox():
    sys.exit(0)

text = "\n".join([command, *python_sources()])
apps = set(re.findall(r"/Applications/([^/\"'\n]+)\.app", text))
if apps:
    statuses = [f"{UPDATES}/{app}/updates/0/update.status" for app in sorted(apps)]
else:
    # Selenium and wpt pick an installed Firefox themselves; check them all.
    statuses = sorted(glob.glob(f"{UPDATES}/*/updates/0/update.status"))

for status in statuses:
    if os.path.exists(status):
        app_name = status[len(UPDATES) + 1 :].split("/")[0]
        print(
            f"{app_name} has a staged update ({status} exists). Ask the user to restart "
            f"{app_name}, and don't launch it via WebDriver until that file is gone.",
            file=sys.stderr,
        )
        sys.exit(2)
