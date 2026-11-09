"""Where the builder finds its inputs and puts its output. build.py sets these from its arguments."""
import os

ROM = "baserom.nds"                     # the original Japanese ROM (see README for its SHA-1)
OUT = "out/DeltoraQuest_EN.nds"         # the English ROM
VERSION = "version_number.txt"         # the patch's version: shown on the title screen, names the release
FONTS = os.environ.get("DELTORA_FONTS", "C:/Windows/Fonts")   # Segoe UI, Arial and Georgia, for a few graphics


def font(name):
    """A system font the graphics patches draw with. They aren't redistributable, so they're
    read from the machine: Windows has them in C:/Windows/Fonts; elsewhere set DELTORA_FONTS."""
    path = os.path.join(FONTS, name)
    if not os.path.exists(path):
        # Windows file names are case-insensitive; other systems' copies may differ in case
        for f in os.listdir(FONTS) if os.path.isdir(FONTS) else ():
            if f.lower() == name.lower():
                return os.path.join(FONTS, f)
    return path
