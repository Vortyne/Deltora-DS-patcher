"""Write the English text, by area, for the web page that reviews the translation (docs/translation.html).

    python tools/export_translation.py site/translation.json

Only the English goes out: translation/en with translation/adjustments.json applied, as the build
uses it. The game's Japanese script isn't ours to publish. The Pages workflow runs this on every
deploy, so the page always shows the translation the patch is built from.
"""
import glob
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
AREAS = (
    ("Opening & Ending", 2178), ("Prologue", 2179), ("Forests of Silence", 2180), ("Mokeet's Mansion", 2181),
    ("Lake of Tears", 2182), ("City of the Rats", 2183), ("Shifting Sands", 2184), ("Dread Mountain", 2185),
    ("Maze of the Beast", 2186), ("Valley of the Lost", 2187), ("Return to Del", 2188),
    ("Mixing Room", 2189), ("Grand Farm", 2190), ("Tom's Shop", 2195), ("Smithing", 2196),
    ("Tower of Illusion", 2194), ("Items & Recipes", 2191), ("Monster Notes", 2193), ("Title & Intro", 2199),
    ("Save & Stage Names", 2192), ("Menus & Labels", 2197), ("Options", 2198), ("Wireless", 2200),
)
LEFT_OUT = {2197: range(25, 72)}        # the developers' debug menus, left in Japanese


def strings(bank, adjust):
    out = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "translation", "en", f"{bank}*.json"))):
        out.update(json.load(open(path, encoding="utf-8")))
    for key, text in adjust.items():
        b, sid = key.split("/")
        if int(b) == bank:
            out[sid] = text
    skip = LEFT_OUT.get(bank, ())
    return [[int(k), v] for k, v in sorted(out.items(), key=lambda kv: int(kv[0])) if v.strip() and int(k) not in skip]


def main(dest):
    adjust_path = os.path.join(ROOT, "translation", "adjustments.json")
    adjust = json.load(open(adjust_path, encoding="utf-8")) if os.path.exists(adjust_path) else {}
    version_path = os.path.join(ROOT, "version_number.txt")
    data = {
        "version": open(version_path).read().strip() if os.path.exists(version_path) else "",
        "areas": [{"name": name, "bank": bank, "rows": strings(bank, adjust)} for name, bank in AREAS],
    }
    os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)
    with open(dest, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print("wrote", dest, sum(len(a["rows"]) for a in data["areas"]), "lines")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "site/translation.json")
