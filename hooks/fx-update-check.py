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

# Firefox stages updates per install: <UPDATES>/<bundle path without .app>/updates/0.
UPDATES = os.path.expanduser("~/Library/Caches/Mozilla/updates")

hook_input = json.load(sys.stdin)
command = hook_input.get("tool_input", {}).get("command", "")
cwd = hook_input.get("cwd") or os.getcwd()


SEPARATORS = set(";&|()\n")
WRAPPERS = {"env", "exec", "nohup", "time", "caffeinate"}
PYTHON = re.compile(r"python[\d.]*$")


def simple_commands():
    """Split the command into simple commands' word lists, dropping redirections."""
    lex = shlex.shlex(command, posix=True, punctuation_chars="();<>|&\n")
    lex.whitespace = " \t"
    lex.whitespace_split = True
    try:
        tokens = list(lex)
    except ValueError:
        tokens = command.split()
    words = []
    skip = False
    for token in tokens:
        if set(token) <= SEPARATORS:
            if words:
                yield words
            words = []
        elif set(token) <= set("<>&"):
            skip = True
        elif skip:
            skip = False
        else:
            words.append(token)
    if words:
        yield words


def scripts_run():
    """Yield (inline code, None) or (None, script path) for each Python program the command
    runs: `python [opts] script.py`, `python -c CODE` or `./script.py`, possibly after `env`,
    `uv run` and the like. Arguments naming .py files (`git add x.py`) don't count."""
    for words in simple_commands():
        i = 0
        while i < len(words):
            w = words[i]
            if re.match(r"\w+=", w) or w in WRAPPERS or (w == "run" and i and words[i - 1] == "uv"):
                i += 1
            elif w == "uv" and i + 1 < len(words) and words[i + 1] == "run":
                i += 1
            elif w.startswith("-") and i and words[i - 1] in WRAPPERS:
                i += 1
            else:
                break
        if i >= len(words):
            continue
        if words[i].endswith(".py"):
            yield None, words[i]
        elif PYTHON.match(os.path.basename(words[i])):
            j = i + 1
            while j < len(words):
                w = words[j]
                if w == "-c" and j + 1 < len(words):
                    yield words[j + 1], None
                    break
                if w in ("-m", "-"):
                    break
                j += 2 if w in ("-W", "-X") else 1
                if not w.startswith("-"):
                    yield None, w
                    break


def python_sources():
    """Yield the Python code the command runs, with the modules it imports from its own
    directory."""
    pending = [
        (source, cwd) if path is None else (None, os.path.join(cwd, os.path.expanduser(path)))
        for source, path in scripts_run()
    ]
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

def bundles_in_command():
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    for token in tokens:
        m = re.match(r"((?:~|/)[^\n]*?)\.app(?:/|$)", token)
        if m:
            yield os.path.expanduser(m.group(1))


def bundles_in_sources():
    for source in python_sources():
        for m in re.finditer(r"[\"']((?:~|/)[^\"'\n]*?)\.app(?:/[^\"'\n]*)?[\"']", source):
            yield os.path.expanduser(m.group(1))


# A bundle named in the command (e.g. a local build passed as an argument) wins over defaults in
# the scripts it runs.
bundles = set(bundles_in_command()) or set(bundles_in_sources())
if bundles:
    statuses = [f"{UPDATES}/{b.lstrip('/')}/updates/0/update.status" for b in sorted(bundles)]
else:
    # Selenium and wpt pick an installed Firefox themselves; check them all.
    statuses = sorted(glob.glob(f"{UPDATES}/Applications/*/updates/0/update.status"))

for status in statuses:
    if os.path.exists(status):
        app_name = status[len(UPDATES) + 1 :].split("/updates/0/")[0].split("/")[-1]
        print(
            f"{app_name} has a staged update ({status} exists). Ask the user to restart "
            f"{app_name}, and don't launch it via WebDriver until that file is gone.",
            file=sys.stderr,
        )
        sys.exit(2)
