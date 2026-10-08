"""Look up the numeric issues.chromium.org component ID for a Chromium component name.

Usage: python3 chromium-component-id.py "Blink>Image" ["Blink>HTML" ...]

Finds directories owned by the component in Chromium's published component map, then reads
`buganizer_public.component_id` from one of their DIR_METADATA files on Gitiles.
"""

import base64
import json
import re
import sys
import urllib.request

MAP_URL = "https://storage.googleapis.com/chromium-owners/component_map.json"
GITILES = "https://chromium.googlesource.com/chromium/src/+/main/{}/DIR_METADATA?format=TEXT"


def component_id(dir_to_component, name):
    dirs = sorted(d for d, c in dir_to_component.items() if c == name)
    if not dirs:
        return None, "no directories with this component"
    for d in dirs[:5]:
        try:
            text = base64.b64decode(urllib.request.urlopen(GITILES.format(d)).read()).decode()
        except Exception:
            continue
        m = re.search(r"buganizer_public[^{]*\{[^}]*component_id:\s*(\d+)", text)
        if m:
            return m.group(1), d
    return None, f"no buganizer_public.component_id in DIR_METADATA of {dirs[:5]}"


def main():
    names = sys.argv[1:]
    if not names:
        sys.exit(__doc__)
    dir_to_component = json.load(urllib.request.urlopen(MAP_URL))["dir-to-component"]
    for name in names:
        cid, where = component_id(dir_to_component, name)
        if cid:
            print(f"{name}\t{cid}\t(from {where}/DIR_METADATA)")
        else:
            close = sorted({c for c in dir_to_component.values() if name.lower() in c.lower()})[:10]
            print(f"{name}\tnot found: {where}; similar: {close}")


if __name__ == "__main__":
    main()
