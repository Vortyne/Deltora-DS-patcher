"""Collision fixes for stage maps, for the D-pad.

A map file (LZ10) holds w x h tiles: 16 bytes of header, four u16 graphics layers, then a u32
per tile whose low nibble is its collision: 0 open, 1 solid, 2-9 corner pieces, 10-13 slopes.
A diagonal gap one tile wide stops a D-pad walk, so these gaps get a second tile.
"""
import struct

from lf2 import lz10

OPEN, SOLID, SLOPE = 0, 1, 10        # SLOPE: the one already on that bush edge; solid at the bottom right
BLSLOPE = 11                         # solid at the bottom left
LSLOPE = 12                          # the slope on the other side of such a corridor; solid at the top left
RSLOPE = 13                          # solid at the top right
# a shallow corner pair (two tiles a row step) as one 45-degree slope and an open tile:
# the pair's first piece -> (left tile, right tile)
PAIR_FIX = {2: (LSLOPE, OPEN), 4: (OPEN, RSLOPE), 6: (OPEN, SLOPE), 8: (BLSLOPE, OPEN)}


def pairs(at):
    """[(x, y, was, now)] for corner pairs whose first piece is at each (x, y, piece)."""
    return [f for x, y, v in at for f in ((x, y, v, PAIR_FIX[v][0]), (x + 1, y, v + 1, PAIR_FIX[v][1]))]


# Lief's house (prologue, chapter 8 and the final chapter): every wall a staircase of pairs;
# right of Jasmine (tile 25, 17) a walk couldn't get back out, only a run
LIEF_HOUSE_PAIRS = ((8, 10, 2), (13, 10, 4), (5, 11, 2), (3, 12, 2), (15, 13, 4), (2, 14, 8),
                    (21, 14, 2), (23, 14, 4), (4, 15, 8), (17, 15, 4), (19, 15, 2), (25, 15, 4),
                    (26, 17, 6), (4, 18, 2), (24, 18, 6), (4, 19, 8), (7, 19, 6), (12, 19, 8),
                    (22, 19, 6), (14, 20, 8), (20, 20, 6), (16, 21, 8), (18, 21, 6))
# Valley of the Lost's 4, 5 corner pairs (the 4's place)
RSTEPS = ((118, 6), (121, 7), (75, 7), (115, 38), (118, 39), (120, 40), (82, 50), (87, 51),
          (86, 82), (89, 83), (92, 84))
# map file: [(x, y, collision was, collision now)]
FIXES = {
    1104: [     # Dread Mountain, stage 1 area 3
        # the corridor below the bushes' slope: its top was capped by corner pieces
        (54, 43, 4, OPEN), (55, 43, 5, OPEN),
        # the diagonal channel at the left: its right slope moves a tile right
        (9, 81, SLOPE, OPEN), (10, 81, SOLID, SLOPE),
        (8, 82, SLOPE, OPEN), (9, 82, SOLID, SLOPE),
        (8, 83, SOLID, SLOPE),
    ],
    1108: [     # Dread Mountain, stage 3 area 1: four diagonal corridors, each made two tiles wide
        # left of centre, rows 31-33: the right slope moves a tile right, one straight line
        (19, 31, SLOPE, OPEN), (20, 31, SOLID, SLOPE),
        (18, 32, SLOPE, OPEN), (19, 32, SOLID, SLOPE),
        (17, 33, SLOPE, OPEN), (18, 33, SOLID, SLOPE),
        # centre, rows 31-35 were one tile wide: the left slope moves a tile left
        (54, 31, LSLOPE, OPEN), (53, 31, SOLID, LSLOPE),
        (53, 32, LSLOPE, OPEN), (52, 32, SOLID, LSLOPE),
        (52, 33, LSLOPE, OPEN), (51, 33, SOLID, LSLOPE),
        (51, 34, LSLOPE, OPEN), (50, 34, SOLID, LSLOPE),
        (50, 35, LSLOPE, OPEN), (49, 35, SOLID, LSLOPE),
        # right of centre, rows 30-33 likewise; row 33's two corner pieces become the slope
        (82, 30, LSLOPE, OPEN), (81, 30, SOLID, LSLOPE),
        (81, 31, LSLOPE, OPEN), (80, 31, SOLID, LSLOPE),
        (80, 32, LSLOPE, OPEN), (79, 32, SOLID, LSLOPE),
        (78, 33, 2, LSLOPE), (79, 33, 3, OPEN),
        # lower right, rows 60-64: the right slope moves a tile right; row 60's corner pieces too
        (89, 60, 6, OPEN), (90, 60, 7, SLOPE),
        (88, 61, SLOPE, OPEN), (89, 61, SOLID, SLOPE),
        (87, 62, SLOPE, OPEN), (88, 62, SOLID, SLOPE),
        (86, 63, SLOPE, OPEN), (87, 63, SOLID, SLOPE),
        (85, 64, SLOPE, OPEN), (86, 64, SOLID, SLOPE),
    ],
    # Valley of the Lost, stage 2 area 1: every pair of shallow corner pieces snagged the D-pad,
    # so each becomes one 45-degree slope and a step. Pieces 2, 3 have the wall above and left:
    # 2 becomes slope 12 (solid top left), 3 opens. Pieces 4, 5 have it above and right:
    # 4 opens, 5 becomes slope 13 (solid top right).
    1130: [(x, y, 2, LSLOPE) for x, y in ((75, 83), (103, 83), (99, 84), (109, 50), (104, 51))]
        + [(x + 1, y, 3, OPEN) for x, y in ((75, 83), (103, 83), (99, 84), (109, 50), (104, 51))]
        + [(x, y, 4, OPEN) for x, y in RSTEPS]
        + [(x + 1, y, 5, RSLOPE) for x, y in RSTEPS],
    1670: pairs(LIEF_HOUSE_PAIRS),
}


def lz10_pack(data):
    """LZ10, greedy: each step takes the longest match (3-18 bytes, up to 4096 back) found
    among earlier places with the same next three bytes."""
    out = bytearray(struct.pack("<I", 0x10 | len(data) << 8))
    seen = {}
    i = 0
    while i < len(data):
        flag_at = len(out)
        out.append(0)
        for bit in range(8):
            if i >= len(data):
                break
            best, back = 0, 0
            for j in reversed(seen.get(data[i:i + 3], [])):
                if i - j > 0x1000:
                    break
                n = 0
                while n < 18 and i + n < len(data) and data[j + n] == data[i + n]:
                    n += 1
                if n > best:
                    best, back = n, i - j
                    if n == 18:
                        break
            step = best if best >= 3 else 1
            if best >= 3:
                out[flag_at] |= 0x80 >> bit
                out += bytes(((best - 3) << 4 | (back - 1) >> 8, (back - 1) & 0xFF))
            else:
                out.append(data[i])
            for k in range(i, i + step):
                seen.setdefault(data[k:k + 3], []).append(k)
            i += step
    return bytes(out + bytes(-len(out) % 4))


def patch(fid, packed):
    m = bytearray(lz10(packed))
    w, h = struct.unpack_from("<HH", m, 4)
    for x, y, was, now in FIXES[fid]:
        at = 16 + w * h * 8 + (y * w + x) * 4
        v = struct.unpack_from("<I", m, at)[0]
        assert v & 15 == was, (fid, x, y, v & 15)
        struct.pack_into("<I", m, at, v & ~15 | now)
    out = lz10_pack(bytes(m))
    assert lz10(out) == bytes(m)
    return out


# Save points: coming back from one puts the player 12 pixels below it, and these put them on a
# wall or a diagonal edge, where the D-pad can't move them (the stylus still could).
# script: [(camp id, x, y as was, x, y now)], each CampSet/CampSet2 call with those arguments
CAMP_RETURN = 12
CAMPS = {
    2447: [(24, 27, 151, 27, 143)],     # Mokeet's Mansion (map 1214): back at y 163 was the ledge's solid edge
    2508: [(28, 996, 661, 988, 661)],   # chapter 6 (map 1120): back on a corner piece's edge
    2535: [(33, 605, 671, 597, 671)],   # chapter 8 (map 1148): back on a slope's edge
}


def patch_camps(fid, script):
    b = bytearray(script)
    n = 0
    for cid, x, y, nx, ny in CAMPS[fid]:
        for at in range(0, len(b) - 15, 2):
            k1, v1, k2, v2, k3, v3, call = struct.unpack_from("<7H", b, at)
            if (k1, k2, k3) in {(a, c, d) for a in (0x4000, 0x4001) for c in (0x4000, 0x4001) for d in (0x4000, 0x4001)}                     and (v1, v2, v3, call) == (cid, x, y, 0x2102):
                struct.pack_into("<HHHH", b, at + 4, 0x4001, nx, 0x4001, ny)
                n += 1
    assert n, fid
    return bytes(b), n

