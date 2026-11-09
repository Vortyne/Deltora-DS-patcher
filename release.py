"""Make the release's patch: build the English ROM and put its BPS patch in docs/, the web patcher's
site, named for version_number.txt, in place of any older version's.

    python release.py [path/to/baserom.nds]

Without a path it looks for the Japanese ROM under its standard name next to this file. Then commit
and push the .bps: the push deploys the site with it. Attach the same file to a GitHub release
tagged v<version> for people who patch by hand.
"""
import glob
import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build import NAME  # noqa: E402

ROM_NAME = "Deltora Quest - Nanatsu no Houseki (Japan).nds"
SITE = os.path.join(HERE, "docs")       # the page downloads the patch from its own site


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, ROM_NAME)
    if not os.path.exists(rom):
        sys.exit(f"No ROM at {rom}.\nUsage: python release.py path/to/baserom.nds")
    version = open(os.path.join(HERE, "version_number.txt"), encoding="utf-8").read().strip()
    name = NAME.format(version=version) + ".bps"
    bps = os.path.join(SITE, name)

    subprocess.run([sys.executable, os.path.join(HERE, "build.py"), rom, "--bps", bps], check=True)

    for old in glob.glob(os.path.join(SITE, NAME.format(version="*") + ".bps")):
        if os.path.basename(old) != name:
            os.remove(old)
            print("removed", os.path.basename(old))

    sha1 = hashlib.sha1(open(bps, "rb").read()).hexdigest()
    print(f"""
Release v{version} is ready: docs/{name} ({os.path.getsize(bps):,} bytes, SHA-1 {sha1}).
Next:
  1. Commit and push it: git add docs/{name} && git commit -m "Release v{version}" && git push
     The push deploys the web patcher with it.
  2. Publish a GitHub release tagged v{version} with docs/{name} attached.""")


if __name__ == "__main__":
    main()
