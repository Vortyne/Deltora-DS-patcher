"""Rebuild the ROM with replaced LF2 entries.

Replaced files are appended after FILEDATA's old end. To make room, _dtq.vx is
moved to the end of the used ROM space, which frees 2.3 MB straight after
FILEDATA. With no replacements the output is byte-identical to the input.
"""
import struct


FAT_VX, FAT_FILEDATA = 4, 5
ROM_CAP = 134217728


def crc16(data):
    crc = 0xFFFF
    for c in data:
        crc ^= c
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


def u32(b, o):
    return struct.unpack_from("<I", b, o)[0]


def build(rom_in, replacements=None, arm9=None):
    """replacements: {lf2_id: bytes}. arm9: replacement ARM9, which may be larger."""
    rom = bytearray(rom_in)
    fat = u32(rom, 0x48)
    if arm9 is not None:
        off, old = u32(rom, 0x20), u32(rom, 0x2C)
        footer = bytes(rom[off + old:off + old + 12])
        if off + len(arm9) + 12 > u32(rom, 0x50):
            # make room: overlay 0 goes to the end of the ROM, the overlay table into its old space
            s0, e0 = struct.unpack_from("<II", rom, fat)
            new = (u32(rom, 0x80) + 0x1FF) & ~0x1FF
            rom[new:new + e0 - s0] = rom[s0:e0]
            struct.pack_into("<II", rom, fat, new, new + e0 - s0)
            struct.pack_into("<I", rom, 0x80, new + e0 - s0)
            ovt, size = u32(rom, 0x50), u32(rom, 0x54)
            table = bytes(rom[ovt:ovt + size])
            rom[ovt:e0] = bytes([255]) * (e0 - ovt)
            moved = s0 + 0x8000
            rom[moved:moved + size] = table
            struct.pack_into("<I", rom, 0x50, moved)
        assert off + len(arm9) + 12 <= u32(rom, 0x50)
        rom[off:off + len(arm9) + 12] = arm9 + footer
        struct.pack_into("<I", rom, 0x2C, len(arm9))
    if replacements:
        fd_s, fd_e = struct.unpack_from("<II", rom, fat + FAT_FILEDATA * 8)
        vx_s, vx_e = struct.unpack_from("<II", rom, fat + FAT_VX * 8)
        assert vx_s >= fd_e
        used = u32(rom, 0x80)

        new_vx = (used + 0x1FF) & ~0x1FF
        vx = bytes(rom[vx_s:vx_e])
        assert new_vx + len(vx) <= ROM_CAP
        rom[new_vx:new_vx + len(vx)] = vx
        struct.pack_into("<II", rom, fat + FAT_VX * 8, new_vx, new_vx + len(vx))
        new_used = new_vx + len(vx)

        limit = vx_e  # old VX space now belongs to FILEDATA
        rom[vx_s:vx_e] = b"\xFF" * (vx_e - vx_s)
        cur = (fd_e + 3) & ~3
        count, hdr = u32(rom, fd_s + 8), u32(rom, fd_s + 12)
        for fid, data in sorted(replacements.items()):
            assert 0 <= fid < count
            off4, size = struct.unpack_from("<II", rom, fd_s + hdr + fid * 8)
            if len(data) <= size:       # fits where it was: written in place, no new space used
                at = fd_s + off4 * 4
                rom[at:at + size] = data + bytes(size - len(data))
                struct.pack_into("<II", rom, fd_s + hdr + fid * 8, off4, len(data))
                continue
            assert cur + len(data) <= limit, "FILEDATA overflow"
            rom[cur:cur + len(data)] = data
            off4 = (cur - fd_s) // 4
            struct.pack_into("<II", rom, fd_s + hdr + fid * 8, off4, len(data))
            cur = (cur + len(data) + 3) & ~3
        struct.pack_into("<I", rom, fat + FAT_FILEDATA * 8 + 4, cur)
        struct.pack_into("<I", rom, 0x80, new_used)
        struct.pack_into("<H", rom, 0x15E, crc16(rom[:0x15E]))
    return bytes(rom)


if __name__ == "__main__":
    import hashlib
    import sys
    from lf2 import read_lf2
    src = open(sys.argv[1], "rb").read()
    assert crc16(src[:0x15E]) == struct.unpack_from("<H", src, 0x15E)[0], "header CRC check"
    same = build(src)
    assert same == src
    print("identity OK", hashlib.sha1(same).hexdigest())
    # replace one file with a larger blob and read everything back
    test = b"TEST" * 5000
    out = build(src, {2192: test})
    fat = u32(out, 0x48)
    s, e = struct.unpack_from("<II", out, fat + FAT_FILEDATA * 8)
    fd = out[s:e]
    ents = read_lf2(fd)
    orig = src[0x130a00:0x130a00 + 44061128]
    oe = read_lf2(orig)
    diffs = [i for i in range(len(ents)) if fd[ents[i][0]:ents[i][0] + ents[i][1]] != orig[oe[i][0]:oe[i][0] + oe[i][1]]]
    assert diffs == [2192], diffs
    assert fd[ents[2192][0]:ents[2192][0] + ents[2192][1]] == test
    vs, ve = struct.unpack_from("<II", out, fat + FAT_VX * 8)
    ovs, ove = struct.unpack_from("<II", src, u32(src, 0x48) + FAT_VX * 8)
    assert out[vs:ve] == src[ovs:ove]
    assert crc16(out[:0x15E]) == struct.unpack_from("<H", out, 0x15E)[0]
    print("replace OK; FILEDATA end", hex(e), "video moved to", hex(vs), "used", hex(u32(out, 0x80)))
