"""Build the English Deltora Quest DS ROM from your own copy of the Japanese game.

    python build.py path/to/baserom.nds [-o PATH] [--bps [PATH]]

Both files are named for version_number.txt unless a PATH is given:
out/Deltora_Quest_DS_english_patch_full_button_control_v<version>.nds, and with --bps the release's patch, out/Deltora_Quest_DS_english_patch_full_button_control_v<version>.bps.

The ROM's game files are unpacked into work/ (once), every patch in builder/ is applied, and the
English ROM is written. Nothing from the game itself is stored in this repository.
"""
import argparse
import hashlib
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "builder"))

NAME = "Deltora_Quest_DS_english_patch_full_button_control_v{version}"   # the patched game (.nds) and the release's patch (.bps)
BASEROM_SHA1 = "5a28815f68e78e2da5b486951a158a374150e459"    # Deltora Quest: Nanatsu no Houseki (Japan)
FAT_FILEDATA = 5                                              # FILEDATA.BIN, the LF2 archive of game files


def unpack(rom, work):
    """Write each file of the LF2 archive to work/lf2/NNNNN.bin, as the patches read them."""
    import lf2
    fat = struct.unpack_from("<I", rom, 0x48)[0]
    start, end = struct.unpack_from("<II", rom, fat + FAT_FILEDATA * 8)
    blob = rom[start:end]
    os.makedirs(os.path.join(work, "lf2"), exist_ok=True)
    for i, (o, s) in enumerate(lf2.read_lf2(blob)):
        open(os.path.join(work, "lf2", f"{i:05d}.bin"), "wb").write(blob[o:o + s])


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("rom", help="the original Japanese ROM")
    ap.add_argument("-o", "--out", help="where to write the English ROM (default: out/ with its versioned name)")
    ap.add_argument("--bps", nargs="?", const="", metavar="PATH",
                    help="also write the release's BPS patch (default: out/ with its versioned name)")
    args = ap.parse_args()

    version = open(os.path.join(HERE, "version_number.txt"), encoding="utf-8").read().strip()
    name = NAME.format(version=version)
    rom_path = os.path.abspath(args.rom)
    out_path = os.path.abspath(args.out or os.path.join(HERE, "out", name + ".nds"))
    bps_path = None
    if args.bps is not None:
        bps_path = os.path.abspath(args.bps or os.path.join(HERE, "out", name + ".bps"))
    rom = open(rom_path, "rb").read()
    sha1 = hashlib.sha1(rom).hexdigest()
    if sha1 != BASEROM_SHA1:
        sys.exit(f"{args.rom}: SHA-1 {sha1}, expected {BASEROM_SHA1}.\n"
                 "This needs the original Japanese release of Deltora Quest: Nanatsu no Houseki, unmodified.")

    os.chdir(HERE)                      # the patches read work/ and translation/ from here
    marker = os.path.join("work", "lf2", ".from")
    if not os.path.exists(marker) or open(marker).read() != sha1:
        print("unpacking the game's files into work/lf2 ...")
        unpack(rom, "work")
        open(marker, "w").write(sha1)

    import paths
    paths.ROM, paths.OUT = rom_path, out_path
    import make_rom
    make_rom.main()

    if bps_path:
        import bps
        english = open(out_path, "rb").read()
        patch = bps.create(rom, english)
        assert bps.apply(rom, patch) == english     # check it before it's published
        os.makedirs(os.path.dirname(bps_path) or ".", exist_ok=True)
        open(bps_path, "wb").write(patch)
        print("wrote", bps_path, len(patch), f"bytes (v{version}); English ROM SHA-1", hashlib.sha1(english).hexdigest())


if __name__ == "__main__":
    main()
