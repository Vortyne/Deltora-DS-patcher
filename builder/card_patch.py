"""Redraw the chapter and stage title cards in English, keeping their glow style."""
import paths
import math
import struct

import numpy as np
import pixelfont
from PIL import Image, ImageDraw, ImageFilter, ImageFont

REG = paths.font("segoeui.ttf")
BOLD = paths.font("segoeuib.ttf")
SS = 4
W, H = 256, 192
MAX_W = 234

# screen id: (top line, main line, bold style)
CARDS = {
    1694: ("Chapter 1", "Forests of Silence", False),
    1701: ("Chapter 2", "Lake of Tears", False),
    1708: ("Chapter 3", "City of the Rats", False),
    1715: ("Chapter 4", "The Shifting Sands", False),
    1722: ("Chapter 5", "Dread Mountain", False),
    1729: ("Chapter 6", "Maze of the Beast", False),
    1736: ("Chapter 7", "Valley of the Lost", False),
    1743: ("Final Chapter", "Return to Del", False),
    1750: ("", "Campfire", False),
    1757: ("Tom's", "Shop", False),
    1764: ("Jasmine's", "Mixing Room", True),
    1771: ("Special Stage", "Mokeet's Mansion", True),
    1778: ("Jack's", "Grand Farm", False),
    1785: ("Extra Stage", "Tower of Illusion", False),
    1792: ("Secret", "Audio Room", True),
}


def _fit(text, path, size):
    while True:
        f = ImageFont.truetype(path, size * SS)
        if f.getlength(text) / SS <= MAX_W or size <= 12:
            return f
        size -= 1


def luminance(top, main, bold):
    path = BOLD if bold else REG
    hi = Image.new("L", (W * SS, H * SS))
    d = ImageDraw.Draw(hi)
    if top:
        d.text((W * SS // 2, 68 * SS), top, fill=255, font=_fit(top, path, 17), anchor="mm")
    d.text((W * SS // 2, (104 if top else 96) * SS), main, fill=255, font=_fit(main, path, 29), anchor="mm")
    m = hi.resize((W, H), Image.LANCZOS)
    glow = np.asarray(hi.filter(ImageFilter.GaussianBlur(2.2 * SS)).resize((W, H), Image.LANCZOS), dtype=np.float32)
    a = np.asarray(m, dtype=np.float32)
    # bright letter, grey soft halo around it
    return np.clip(a * 1.15 + glow * 0.9, 0, 255)


def patch(rgcn, rlcn, rcsn, top, main, bold):
    b = bytearray(rgcn)
    n = struct.unpack_from("<I", rlcn, 0x20)[0]
    c = struct.unpack_from(f"<{n // 2}H", rlcn, 0x28)
    m = struct.unpack_from("<768H", rcsn, 0x24)
    pb = m[0] >> 12
    shades = np.array([(c[pb * 16 + i] & 31) * 255 / 31 for i in range(16)], dtype=np.float32)
    bg = b[0x30 + (m[0] & 0x3FF) * 32] & 15
    L = luminance(top, main, bold)
    for i, e in enumerate(m):
        ry, rx = i // 32 * 8, i % 32 * 8
        o = 0x30 + (e & 0x3FF) * 32
        for y in range(8):
            for x in range(8):
                v = L[ry + y, rx + x]
                k = bg if v < 6 else int(np.abs(shades[1:] - v).argmin()) + 1
                a = o + y * 4 + x // 2
                b[a] = (b[a] & 0x0F) | k << 4 if x & 1 else (b[a] & 0xF0) | k
    return bytes(b)


def _label(text):
    """32x16 two-colour label: 2 fill, 1 outline, 0 clear."""
    f = ImageFont.truetype(BOLD, 12 * SS)
    hi = Image.new("L", (32 * SS, 16 * SS))
    ImageDraw.Draw(hi).text((16 * SS, 8 * SS), text, fill=255, font=f, anchor="mm")
    a = np.asarray(hi.resize((32, 16), Image.LANCZOS)) > 110
    o = a.copy()
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
        o |= np.roll(np.roll(a, dy, 0), dx, 1)
    px = np.zeros((16, 32), dtype=np.uint8)
    px[o] = 1
    px[a] = 2
    return px


def _label_tiles(text):
    """Encode a label as 8 tiles, 4 across and 2 down."""
    px = _label(text)
    out = bytearray(256)
    for t in range(8):
        for y in range(8):
            for x in range(8):
                v = int(px[t // 4 * 8 + y, t % 4 * 8 + x])
                a = t * 32 + y * 4 + x // 2
                out[a] |= v << 4 if x & 1 else v
    return bytes(out)


def patch_yes_no(rgcn, yes_src, no_src):
    """Replace every copy of the Japanese labels, whatever the tile layout.

    Each row of 4 tiles is matched separately because some files keep the
    two rows apart. yes_src and no_src are the original 256-byte labels.
    Returns the new file and how many rows changed.
    """
    b = bytearray(rgcn)
    n = 0
    for src, text in ((yes_src, "Yes"), (no_src, "No")):
        new = _label_tiles(text)
        for row in (0, 128):
            old = src[row:row + 128]
            if not any(old):
                continue
            o = b.find(old)
            while o >= 0:
                b[o:o + 128] = new[row:row + 128]
                n += 1
                o = b.find(old, o + 128)
    return bytes(b), n


def patch_game_over(rgcn, rlcn, rcsn):
    """Screen 425: replace the red Japanese line."""
    n = struct.unpack_from("<I", rlcn, 0x20)[0]
    c = struct.unpack_from(f"<{n // 2}H", rlcn, 0x28)
    p = np.array([[(x & 31) * 255 / 31, (x >> 5 & 31) * 255 / 31, (x >> 10 & 31) * 255 / 31] for x in c], dtype=np.float32)
    b = bytearray(rgcn)
    s = bytearray(rcsn)
    m = list(struct.unpack_from("<1024H", s, 0x24))
    rgb = np.zeros((192, 256, 3), dtype=np.float32)
    for r in range(24):
        for k in range(32):
            e = m[r * 32 + k]
            o = 0x30 + (e & 0x3FF) * 32
            for y in range(8):
                for x in range(8):
                    by = b[o + y * 4 + x // 2]
                    rgb[r * 8 + y, k * 8 + x] = p[(e >> 12) * 16 + (by >> 4 if x & 1 else by & 15)]
    mask = np.zeros((192, 256), dtype=bool)
    box = (slice(10, 32), slice(2, 176))
    red = rgb[..., 0] > rgb[..., 1] + 45
    mask[box] = red[box]
    for _ in range(3):
        mask |= np.roll(mask, 1, 0) | np.roll(mask, -1, 0) | np.roll(mask, 1, 1) | np.roll(mask, -1, 1)
    known = ~mask
    out = rgb.copy()
    while not known.all():
        acc = np.zeros_like(out)
        cnt = np.zeros((192, 256), dtype=np.float32)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            acc += np.roll(np.roll(out * known[..., None], dy, 0), dx, 1)
            cnt += np.roll(np.roll(known, dy, 0), dx, 1)
        g = ~known & (cnt > 0)
        out[g] = acc[g] / cnt[g][..., None]
        known |= g
    hi = Image.new("L", (256 * SS, 192 * SS))
    ImageDraw.Draw(hi).text((9 * SS, 20 * SS), "Lief and his friends have fallen…", fill=255,
                            font=ImageFont.truetype(BOLD, 12 * SS), anchor="lm")
    a = np.asarray(hi.resize((256, 192), Image.LANCZOS), dtype=np.float32) / 255
    edge = np.asarray(hi.filter(ImageFilter.MaxFilter(SS * 2 + 1)).resize((256, 192), Image.LANCZOS), dtype=np.float32) / 255
    out = out * (1 - edge[..., None]) + np.array((22, 6, 6), dtype=np.float32) * edge[..., None]
    out = out * (1 - a[..., None]) + np.array((222, 34, 24), dtype=np.float32) * a[..., None]
    for r in range(0, 6):
        for k in range(32):
            t = out[r * 8:r * 8 + 8, k * 8:k * 8 + 8].reshape(64, 3)
            if np.abs(t - rgb[r * 8:r * 8 + 8, k * 8:k * 8 + 8].reshape(64, 3)).sum() == 0:
                continue
            best = None
            for pb in range(16):
                d = ((t[:, None, :] - p[pb * 16 + 1:pb * 16 + 16][None]) ** 2).sum(2)
                sc = d.min(1).sum()
                if best is None or sc < best:
                    best, idx, bp = sc, d.argmin(1) + 1, pb
            e = m[r * 32 + k]
            o = 0x30 + (e & 0x3FF) * 32
            for i in range(64):
                y, x = i // 8, i % 8
                q = o + y * 4 + x // 2
                b[q] = (b[q] & 0x0F) | int(idx[i]) << 4 if x & 1 else (b[q] & 0xF0) | int(idx[i])
            m[r * 32 + k] = (e & 0x0FFF) | bp << 12
    struct.pack_into("<1024H", s, 0x24, *m)
    return bytes(b), bytes(s)


NARROW = paths.font("ARIALNB.TTF")


def sprite_label(text, w=32, h=16, size=12, fill=1, edge=15, font=NARROW, soft_fill=2, soft_edge=11):
    """Encode a w x h sprite label as 4bpp tiles in 1D order."""
    hi = Image.new("L", (w * 8, h * 8))
    ImageDraw.Draw(hi).text((w * 4, h * 4), text, fill=255, font=ImageFont.truetype(font, size * 8), anchor="mm")
    cov = np.asarray(hi.resize((w, h), Image.BOX)) / 255
    a = cov >= 0.35
    o = a.copy()
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        o |= np.roll(np.roll(a, dy, 0), dx, 1)
    d = a.copy()
    for dy, dx in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
        d |= np.roll(np.roll(a, dy, 0), dx, 1)
    px = np.zeros((h, w), dtype=np.uint8)
    px[d] = soft_edge if fill == 1 and soft_edge is not None else edge
    px[o] = edge
    px[a] = soft_fill if fill == 1 and soft_fill is not None else fill
    px[cov >= 0.68] = fill
    out = bytearray(w * h // 2)
    n = 0
    for ty in range(h // 8):
        for tx in range(w // 8):
            for y in range(8):
                for x in range(0, 8, 2):
                    out[n] = int(px[ty * 8 + y, tx * 8 + x]) | int(px[ty * 8 + y, tx * 8 + x + 1]) << 4
                    n += 1
    return bytes(out)


SIGN_GREEN = 5 | 28 << 5 | 14 << 10     # close to the camp's selection arrow
SIGN_FREE = 13                          # merged into the near-identical shade 14


def sign_bitmap(rgcn):
    b = rgcn[0x30:0x30 + 2048]
    d = np.zeros((128, 32), dtype=np.uint8)
    for i in range(32 * 128):
        d[i // 32, i % 32] = b[i // 2] >> 4 if i & 1 else b[i // 2] & 15
    return d


def sign_pack(d):
    out = bytearray(d.size // 2)
    for i, v in enumerate(d.flatten().tolist()):
        out[i // 2] |= v << 4 if i & 1 else v
    return bytes(out)


def sign_highlight(rgcn, cells, anim, palette):
    """Give the camp's Save sign a second sequence with a green rim. Returns the four files."""
    d = sign_bitmap(rgcn)
    d[d == SIGN_FREE] = 14
    lit = d.copy()
    for fr in range(4):
        f = lit[fr * 32:fr * 32 + 32]
        solid = f != 0
        grown = np.ones((34, 34), dtype=bool)
        grown[1:33, 1:33] = ~solid
        near = np.zeros((32, 32), dtype=bool)
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            near |= np.roll(np.roll(grown, dy, 0), dx, 1)[1:33, 1:33]
        rim = solid & near
        inner = np.zeros((32, 32), dtype=bool)
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            inner |= np.roll(np.roll(rim, dy, 0), dx, 1)
        f[rim | (inner & solid)] = SIGN_FREE
    data = sign_pack(d) + sign_pack(lit)
    pixels = bytearray(rgcn[:0x30]) + data + rgcn[0x30 + 2048:]
    struct.pack_into("<I", pixels, 8, len(pixels))
    struct.pack_into("<I", pixels, 0x14, 0x20 + len(data))
    struct.pack_into("<I", pixels, 0x28, len(data))

    pal = bytearray(palette)
    struct.pack_into("<H", pal, 0x28 + SIGN_FREE * 2, SIGN_GREEN)

    # cells: entries, then one OAM per cell, then the transfer table
    tail = cells[0x90:]
    oam = cells[0x50:0x56]
    body = bytearray(struct.pack("<HHIII", 8, 0, 0x18, 2, 0) + bytes(8))
    entries = b"".join(struct.pack("<HHI", 1, 6, i * 6) for i in range(8))
    oams = oam * 8
    table_at = 0x18 + len(entries) + len(oams)
    struct.pack_into("<I", body, 12, table_at)
    table = struct.pack("<II", 0x200, 8) + bytes(4) * 0
    table = cells[0x68:0x70] + b"".join(struct.pack("<II", i * 0x200, 0x200) for i in range(8))
    section = bytes(body) + entries + oams + table
    out = bytearray(cells[:0x10]) + b"KBEC" + struct.pack("<I", 8 + len(section)) + section + tail
    struct.pack_into("<I", out, 8, len(out))

    # animation: the second sequence plays the same steps on cells 4 to 7
    frames = anim[0x40:0x70]
    second = bytearray(frames)
    for i in range(0, len(second), 8):
        off = struct.unpack_from("<I", second, i)[0]
        struct.pack_into("<I", second, i, off + 8)
    seq = bytearray(anim[0x30:0x40])
    struct.pack_into("<I", seq, 12, len(frames))
    head = struct.pack("<HHIII", 2, 12, 0x18, 0x38, 0x38 + 96) + bytes(8)
    data = struct.pack("<8H", *range(8))
    section = head + bytes(anim[0x30:0x40]) + bytes(seq) + frames + bytes(second) + data
    tail = anim[0x78:]
    timing = bytearray(anim[:0x10]) + b"KNBA" + struct.pack("<I", 8 + len(section)) + section + tail
    struct.pack_into("<I", timing, 8, len(timing))
    return bytes(pixels), bytes(out), bytes(timing), bytes(pal)


YN_BLUE, YN_BROWN = 14, 12      # rarely used shades, merged into 3 and 15
YN_COLOURS = {YN_BLUE: 15 | 25 << 5 | 31 << 10, YN_BROWN: 29 | 18 << 5 | 6 << 10}
YN_CELL = 0x900                 # 32x16 label, then 64x64 portrait
YN_ARROWS = 0x100               # two 16x16 arrows


def yn_read(b, o, w, h, tiled):
    a = np.zeros((h, w), dtype=np.uint8)
    for i in range(w * h):
        v = b[o + i // 2]
        v = v >> 4 if i & 1 else v & 15
        if tiled:
            n = w // 8
            t, py, px = i // 64, i % 64 // 8, i % 8
            a[t // n * 8 + py, t % n * 8 + px] = v
        else:
            a[i // w, i % w] = v
    return a


def yn_write(a, tiled):
    h, w = a.shape
    out = bytearray(w * h // 2)
    for i in range(w * h):
        if tiled:
            n = w // 8
            t, py, px = i // 64, i % 64 // 8, i % 8
            v = int(a[t // n * 8 + py, t % n * 8 + px])
        else:
            v = int(a[i // w, i % w])
        out[i // 2] |= v << 4 if i & 1 else v
    return bytes(out)


def yn_arrow(right):
    """A 16x16 pointer in the labels' colours, pointing at the label."""
    a = np.zeros((16, 16), dtype=np.uint8)
    for i in range(6):
        col = 5 + i if right else 10 - i
        a[8 - 6 + i:8 + 6 - i, col] = 15
    o = a != 0
    edge = np.zeros_like(o)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        edge |= np.roll(np.roll(o, dy, 0), dx, 1)
    a[edge & ~o] = 1
    return a


def yn_frames(rgcn, tiled):
    """Base frames with the two freed shades merged, plus the four selected frames."""
    b = rgcn[0x30:0x30 + 6 * YN_CELL]
    base, lit = bytearray(), bytearray()
    for n in range(6):
        o = n * YN_CELL
        label = yn_read(b, o, 32, 16, tiled)
        art = yn_read(b, o + 0x100, 64, 64, tiled)
        for im in (label, art):
            im[im == YN_BROWN] = 15
            im[im == YN_BLUE] = 3
        base += yn_write(label, tiled) + yn_write(art, tiled)
        if n in (1, 4):
            continue
        sel = art.copy()
        ring = np.ones((64, 64), dtype=bool)
        ring[3:61, 3:61] = False
        sel[ring & (art == 9)] = YN_BLUE
        sel[ring & (art == 4)] = YN_BROWN
        lit += yn_write(label, tiled) + yn_write(sel, tiled)
        lit += yn_write(yn_arrow(True), tiled) + yn_write(yn_arrow(False), tiled)
    return bytes(base), bytes(lit)


def yn_grow(rgcn, tiled):
    base, lit = yn_frames(rgcn, tiled)
    data = base + lit
    out = bytearray(rgcn[:0x30]) + data + rgcn[0x30 + 6 * YN_CELL:]
    struct.pack_into("<I", out, 8, len(out))
    struct.pack_into("<I", out, 0x14, 0x20 + len(data))
    struct.pack_into("<I", out, 0x28, len(data))
    return bytes(out)


def yes_no_highlight(tiles, bitmap, cells, anim, palette):
    """Selected Yes and No: sequences 2 and 3 use new cells with arrows and a bright rim."""
    new_size = YN_CELL + YN_ARROWS
    old_oam = cells[0x60:0x60 + 72]
    label, art = old_oam[:6], old_oam[6:12]
    left = struct.pack("<HHH", 0x00D0, 0x41E0, 0x12)
    right = struct.pack("<HHH", 0x00D0, 0x4010, 0x13)
    entries = cells[0x30:0x60] + b"".join(struct.pack("<HHI", 4, 0xD, 72 + i * 24) for i in range(4))
    oams = old_oam + (label + art + left + right) * 4
    table_at = 0x18 + len(entries) + len(oams)
    table = struct.pack("<II", new_size, 8)
    table += b"".join(struct.pack("<II", i * YN_CELL, YN_CELL) for i in range(6))
    table += b"".join(struct.pack("<II", 6 * YN_CELL + i * new_size, new_size) for i in range(4))
    head = struct.pack("<HHIII", 10, 0, 0x18, 2, table_at) + bytes(8)
    section = head + entries + oams + table
    grid = bytearray(cells[:0x10]) + b"KBEC" + struct.pack("<I", 8 + len(section)) + section + cells[0xE0:]
    struct.pack_into("<I", grid, 8, len(grid))

    seqs = anim[0x30:0x50]
    frames = anim[0x50:0x70]
    seq2 = bytearray(seqs[:16])
    struct.pack_into("<I", seq2, 12, 0x20)
    seq3 = bytearray(seqs[:16])
    struct.pack_into("<I", seq3, 12, 0x30)
    more = bytearray()
    for i, (off, dur) in enumerate(((8, 20), (10, 10), (12, 15), (14, 15))):
        more += struct.pack("<IHH", off, dur, 0xBEEF)
    head = struct.pack("<HHIII", 4, 8, 0x18, 0x58, 0x98) + bytes(8)
    data = anim[0x70:0x78] + struct.pack("<4H", 6, 7, 8, 9)
    section = head + seqs + bytes(seq2) + bytes(seq3) + frames + bytes(more) + data
    timing = bytearray(anim[:0x10]) + b"KNBA" + struct.pack("<I", 8 + len(section)) + section + anim[0x78:]
    struct.pack_into("<I", timing, 8, len(timing))

    pal = bytearray(palette)
    for index, colour in YN_COLOURS.items():
        struct.pack_into("<H", pal, 0x28 + index * 2, colour)
    return yn_grow(tiles, True), yn_grow(bitmap, False), bytes(grid), bytes(timing), bytes(pal)


PROMPT_CELL = 0x300             # 32x32, then a 32x16 piece
PROMPT_HEIGHTS = (4, 4, 3, 2, 0, 1)     # how far the button stands up in each cell


def prompt_frame(height):
    """A grey button on its base with an embossed A; it flashes white when pressed down."""
    a = np.zeros((32, 32), dtype=np.uint8)
    disc = lambda cy, r: [(y, x) for y in range(32) for x in range(32)
                          if (x - 15.5) ** 2 + (y - cy) ** 2 <= r * r]
    base = 20.5
    for y, x in disc(base, 11.2):
        a[y, x] = 15
    for h in range(height + 1):
        for y, x in disc(base - h, 10.2):
            a[y, x] = 14
    top = base - height
    face, light, shade = (2, 1, 3) if height < 2 else (3, 2, 14)
    for y, x in disc(top, 9.2):
        a[y, x] = face
    letter = ["...##...", "..####..", ".##..##.", ".##..##.", ".######.", ".##..##.", ".##..##."]
    oy, ox = int(top) - 3, 12
    for dy, dx, shade_or_light in ((1, 1, shade), (0, 0, light)):
        for y, row in enumerate(letter):
            for x, c in enumerate(row):
                if c == "#":
                    a[oy + y + dy, ox + x + dx] = shade_or_light
    return a


def prompt_button(tiles, bitmap, cells):
    """Replace the stylus prompt's art. Returns the two graphics files and the cells."""
    files = []
    for rgcn, tiled in ((tiles, True), (bitmap, False)):
        out = bytearray(rgcn)
        for n, h in enumerate(PROMPT_HEIGHTS):
            o = 0x30 + n * PROMPT_CELL
            out[o:o + 0x200] = yn_write(prompt_frame(h), tiled)
            out[o + 0x200:o + PROMPT_CELL] = bytes(0x100)
        files.append(bytes(out))
    grid = bytearray(cells)
    for n in range(6):
        struct.pack_into("<HH", grid, 0x60 + n * 12, 0x00E8, 0x81F0)    # stay in one place
    return files[0], files[1], bytes(grid)


# per cell, in files 5309 to 5311
MENU_LABELS = (["Material"] * 3 + ["Equip"] * 3 + ["Key Item"] * 3 + [None] * 3
               + ["Cards"] * 3 + ["Item"] * 3)


def menu_label(text):
    """A 64x16 label in the dialogue font, with a dark outline."""
    letters = plate_text(text, 1)
    a = np.zeros((16, 64), dtype=bool)
    x = (64 - letters.shape[1]) // 2
    a[3:3 + letters.shape[0], x:x + letters.shape[1]] = letters
    o = a.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            o |= np.roll(np.roll(a, dy, 0), dx, 1)
    px = np.zeros((16, 64), dtype=np.uint8)
    px[o] = 15
    px[a] = 1
    return px


def menu_frames(rgcn, table, tiled):
    data = bytearray()
    for text, (off, size) in zip(MENU_LABELS, table):
        art = rgcn[0x30 + off:0x30 + off + size]
        if text:
            px = menu_label(text)
            data += yn_write(px[:, :32], tiled) + yn_write(px[:, 32:], tiled)
            art = art[0x100:]
        data += art
    out = bytearray(rgcn[:0x30]) + data + rgcn[0x30 + 0x3300:]
    struct.pack_into("<I", out, 8, len(out))
    struct.pack_into("<I", out, 0x14, 0x20 + len(data))
    struct.pack_into("<I", out, 0x28, len(data))
    return bytes(out)


def menu_labels(tiles, bitmap, cells):
    """Give each bag icon a 64x16 label: two 32x16 sprites where there was one."""
    n, _, entries_at, _, table_at = struct.unpack_from("<HHIII", cells, 0x18)
    entries_at += 0x18
    oams = entries_at + n * 8
    table_at += 0x18
    old = [struct.unpack_from("<II", cells, table_at + 8 + i * 8) for i in range(n)]
    entries, sprites, frames, at = b"", b"", b"", 0
    for i, text in enumerate(MENU_LABELS):
        count, attr, off = struct.unpack_from("<HHI", cells, entries_at + i * 8)
        size = 0x200
        if text:
            art = bytearray(cells[oams + off + 6:oams + off + 12])
            struct.pack_into("<H", art, 4, 4)
            sprites_here = struct.pack("<HHHHHH", 0x4010, 0x81E0, 0, 0x4010, 0x8000, 2) + bytes(art)
            count, attr, size = 3, 0xD, 0x400
        else:
            sprites_here = cells[oams + off:oams + off + count * 6]
        entries += struct.pack("<HHI", count, attr, len(sprites))
        sprites += sprites_here
        frames += struct.pack("<II", at, size)
        at += size
    table = struct.pack("<II", 0x400, 8) + frames
    head = struct.pack("<HHIII", n, 0, 0x18, 2, 0x18 + len(entries) + len(sprites)) + bytes(8)
    section = head + entries + sprites + table
    grid = bytearray(cells[:0x10]) + b"KBEC" + struct.pack("<I", 8 + len(section)) + section +         cells[0x10 + struct.unpack_from("<I", cells, 0x14)[0]:]
    struct.pack_into("<I", grid, 8, len(grid))
    return menu_frames(tiles, old, True), menu_frames(bitmap, old, False), bytes(grid)


GEAR_BACK_CELLS = (9, 10, 11)       # the back button's three frames; the gear copies them
GEAR_FILL = 1                       # the button face


def gear_mask():
    """A 17x17 gear: a ring with a hole and 8 square teeth."""
    m = np.zeros((32, 32), dtype=bool)
    for y in range(32):
        for x in range(32):
            dx, dy = x - 15.5, y - 15.5
            r = (dx * dx + dy * dy) ** 0.5
            teeth = any(4 < dx * c + dy * s_ <= 8.4 and abs(dy * c - dx * s_) <= 1.6
                        for c, s_ in ((math.cos(k * math.pi / 4), math.sin(k * math.pi / 4)) for k in range(8)))
            if 2.5 < r <= 6.2 or teeth and r > 2.5:
                m[y, x] = True
    return m


def sprite_px(art, tiled):
    px = np.zeros((32, 32), dtype=np.uint8)
    for i in range(1024):
        v = art[i // 2] >> 4 if i & 1 else art[i // 2] & 15
        if tiled:
            t, py, qx = i // 64, i % 64 // 8, i % 8
            px[t // 4 * 8 + py, t % 4 * 8 + qx] = v
        else:
            px[i // 32, i % 32] = v
    return px


def menu_gear(anim, tiles, bitmap, cells):
    """An options button for the bag's top page: the back button's box, frames and colours,
    with a gear instead of the arrow. Cells 18 to 20 and sequence 6."""
    n, _, entries_at, _, table_at = struct.unpack_from("<HHIII", cells, 0x18)
    entries_at += 0x18
    table_at += 0x18
    oams = entries_at + n * 8
    frames = [struct.unpack_from("<II", cells, table_at + 8 + i * 8) for i in range(n)]
    gear = gear_mask()
    outs = []
    for rgcn, tiled in ((tiles, True), (bitmap, False)):
        data = bytearray(rgcn[0x30:0x30 + sum(f[1] for f in frames)])
        size = len(data)
        for c in GEAR_BACK_CELLS:
            off, length = frames[c]
            px = sprite_px(data[off:off + length], tiled)
            ink = np.bincount(px[8:26, 8:26].ravel(), minlength=16)
            ink[[0, GEAR_FILL, 15]] = 0
            colour = int(ink.argmax())          # the arrow's shade in this frame
            px[(px == colour)] = GEAR_FILL
            px[gear] = colour
            data += yn_write(px, tiled)
        out = bytearray(rgcn[:0x30]) + data + rgcn[0x30 + size:]
        struct.pack_into("<I", out, 8, len(out))
        struct.pack_into("<I", out, 0x14, struct.unpack_from("<I", rgcn, 0x14)[0] + len(data) - size)
        struct.pack_into("<I", out, 0x28, len(data))
        outs.append(bytes(out))
        new_size = len(data)
    entries = cells[entries_at:entries_at + n * 8]
    sprites = cells[oams:table_at]
    back_count, back_attr, back_off = struct.unpack_from("<HHI", cells, entries_at + GEAR_BACK_CELLS[0] * 8)
    oam = cells[oams + back_off:oams + back_off + back_count * 6]
    at = size
    for k in range(3):
        entries += struct.pack("<HHI", back_count, back_attr, len(sprites))
        sprites += oam
        frames.append((at, 0x200))
        at += 0x200
    sprites += bytes(-len(sprites) % 4)
    m = n + 3
    table = struct.pack("<II", struct.unpack_from("<I", cells, table_at)[0], 8) + b"".join(struct.pack("<II", *f) for f in frames)
    head = struct.pack("<HHIII", m, 0, 0x18, 2, 0x18 + len(entries) + len(sprites)) + bytes(8)
    section = head + entries + sprites + table
    grid = bytearray(cells[:0x10]) + b"KBEC" + struct.pack("<I", 8 + len(section)) + section +         cells[0x10 + struct.unpack_from("<I", cells, 0x14)[0]:]
    struct.pack_into("<I", grid, 8, len(grid))

    ns, nf, so, fo, do = struct.unpack_from("<HHIII", anim, 0x18)
    end = 0x10 + struct.unpack_from("<I", anim, 0x14)[0]
    seqs = anim[0x18 + so:0x18 + fo]
    frs = anim[0x18 + fo:0x18 + do]
    dat = anim[0x18 + do:end]
    back = struct.unpack_from("<HHIII", seqs, 3 * 16)
    first = back[4] // 8
    gear_data = len(dat)
    dat += struct.pack("<4H", n, n + 1, n + 2, 0xCCCC)
    for k in range(back[0]):
        d_off, dur, pad = struct.unpack_from("<IHH", frs, (first + k) * 8)
        cell = struct.unpack_from("<H", anim, 0x18 + do + d_off)[0] - GEAR_BACK_CELLS[0]
        frs += struct.pack("<IHH", gear_data + cell * 2, dur, pad)
    seqs += struct.pack("<HHIII", back[0], back[1], back[2], back[3], nf * 8)
    body = struct.pack("<HHIII", ns + 1, nf + back[0], 0x18, 0x18 + len(seqs), 0x18 + len(seqs) + len(frs)) + bytes(8)
    body += seqs + frs + dat
    body += bytes(-len(body) % 4)
    na = bytearray(anim[:0x10]) + b"KNBA" + struct.pack("<I", 8 + len(body)) + body + anim[end:]
    struct.pack_into("<I", na, 8, len(na))
    return bytes(na), outs[0], outs[1], bytes(grid)


BOOK_PAGES = (818, 819, 820), (822, 823, 824), (826, 827, 828), (830, 831, 832)   # palette, tiles, map
BOOK_BADGES = (                 # on the corners of each page's raised tab
    (("R", 54, 9),),
    (("L", 62, 9), ("R", 110, 9)),
    (("L", 118, 9), ("R", 166, 9)),
    (("L", 174, 9),),
)


def book_badge(letter):
    """13x12 shoulder button: 0 clear, 1 outline, 2 face, 3 letter."""
    a = np.full((12, 13), 2, dtype=np.uint8)
    a[0] = a[-1] = 1
    a[:, 0] = a[:, -1] = 1
    for y in (0, -1):
        a[y, [0, -1]] = 0
    a[2:10, 4:9][pixelfont.glyph(letter)[:8]] = 3
    return a


def book_buttons(tiles, palette, screen, badges):
    """Paint L and R buttons into a card book page, in greys that replace its rarest shades."""
    pixels = np.frombuffer(tiles, np.uint8, 0x8000, 0x30)
    pixels = np.stack([pixels & 15, pixels >> 4], 1).reshape(1024, 64)
    grid = np.frombuffer(screen, "<u2", 1024, 0x24).astype(int)
    pal = bytearray(palette)
    colours = np.frombuffer(palette, "<u2", 256, 0x28).astype(int)
    rgb = np.stack([colours & 31, colours >> 5 & 31, colours >> 10 & 31], 1)
    spots = [(left + x, top + y, v, letter) for letter, left, top in badges
             for (y, x), v in np.ndenumerate(book_badge(letter) if isinstance(letter, str) else letter) if v]
    rows = {int(grid[y // 8 * 32 + x // 8]) >> 12 for x, y, _, _ in spots}
    greys = {}
    for row in rows:
        own = sorted({int(e) & 1023 for e in grid if int(e) >> 12 == row})
        use = np.bincount(pixels[own].flatten(), minlength=16)[1:16]
        free = [int(i) + 1 for i in np.argsort(use)[:3]]
        keep = [i for i in range(1, 16) if i not in free]
        for i in free:
            d = ((rgb[row * 16 + np.array(keep)] - rgb[row * 16 + i]) ** 2).sum(1)
            part = pixels[own]
            part[part == i] = keep[int(d.argmin())]
            pixels[own] = part
        for i, colour in zip(free, (3 | 3 << 5 | 3 << 10, 21 | 21 << 5 | 19 << 10, 31 | 31 << 5 | 29 << 10)):
            struct.pack_into("<H", pal, 0x28 + (row * 16 + i) * 2, colour)
        greys[row] = free
    for x, y, v, _ in spots:
        entry = int(grid[y // 8 * 32 + x // 8])
        ix = 7 - x % 8 if entry & 0x400 else x % 8
        iy = 7 - y % 8 if entry & 0x800 else y % 8
        pixels[entry & 1023, iy * 8 + ix] = greys[entry >> 12][int(v) - 1]
    packed = (pixels[:, 0::2] | pixels[:, 1::2] << 4).astype(np.uint8).tobytes()
    return tiles[:0x30] + packed + tiles[0x8030:], bytes(pal)


# cells, tiles, palette, small line, name
MOVE_TITLES = (
    (5505, 5506, 5507, None, "First Slash"),
    (5509, 5510, 5507, None, "Flash Slash"),
    (5512, 5513, 5507, None, "Spinning Cut"),
    (5515, 5516, 5507, None, "Zeta Slash"),
    (5518, 5519, 5507, None, "Final Slash"),
    (5526, 5527, 5528, None, "Help Me, Kree!"),
    (5530, 5531, 5528, None, "Forest Dance"),
    (5533, 5534, 5528, None, "Lend a Hand, Kree!"),
    (5536, 5537, 5528, None, "Jungle Dance"),
    (5539, 5540, 5528, None, "Dance of Blade and Kree"),
    (5542, 5543, 5544, "Palace Guard Style", "Gale"),
    (5546, 5547, 5544, "Palace Guard Style", "Blaze"),
    (5549, 5550, 5544, "Palace Guard Style", "Lightning"),
    (5552, 5553, 5544, "Palace Guard Style", "Landslide"),
    (5555, 5556, 5544, "Palace Guard Secret Art", "Phantom Dream"),
)
MOVE_FONT = paths.font("arialbi.ttf")
OBJ_SIZES = {(0, 0): (8, 8), (0, 1): (16, 16), (0, 2): (32, 32), (0, 3): (64, 64),
             (1, 0): (16, 8), (1, 1): (32, 8), (1, 2): (32, 16), (1, 3): (64, 32),
             (2, 0): (8, 16), (2, 1): (8, 32), (2, 2): (16, 32), (2, 3): (32, 64)}


def move_line(text, width, size):
    """Coverage of one line of bold italic, shrunk to fit width."""
    while True:
        f = ImageFont.truetype(MOVE_FONT, size * 8)
        if f.getlength(text) / 8 <= width or size <= 12:
            break
        size -= 1
    hi = Image.new("L", (int(f.getlength(text)) + 64, size * 12))
    ImageDraw.Draw(hi).text((24, size * 2), text, fill=255, font=f)
    box = hi.getbbox()
    hi = hi.crop(box)
    h = round(hi.height / 8)
    return np.asarray(hi.resize((min(round(hi.width / 8), width), h), Image.BOX)) >= 110


def move_canvas(height, width, small, name):
    """Mask of the title's letters, on a canvas of the sprites' size."""
    a = np.zeros((height, width), dtype=bool)
    big = move_line(name, width - 6, 28 if small is None else 19)
    y = height - big.shape[0] - 3
    x = (width - big.shape[1]) // 2
    a[y:y + big.shape[0], x:x + big.shape[1]] = big
    if small:
        line = plate_text(small, 1, width)
        ly = 1
        lx = x if x + line.shape[1] < width else (width - line.shape[1]) // 2
        a[ly:ly + line.shape[0], lx:lx + line.shape[1]] |= line
    return a


def mash_canvas(height, width):
    """"Mash", a filled circle with an A cut out of it, and "!". Returns the mask and the cut-out."""
    a = np.zeros((height, width), dtype=bool)
    hole = np.zeros((height, width), dtype=bool)
    word = move_line("Mash", width // 2, 28)
    bang = move_line("!", 16, 28)
    h = word.shape[0]
    d = (h + 3) | 1
    letter = move_line("A", d - 8, d - 6)
    total = word.shape[1] + 10 + d + 3 + bang.shape[1]
    x = (width - total) // 2
    y = height - h - 3
    a[y:y + h, x:x + word.shape[1]] = word
    x += word.shape[1] + 10
    top = max(0, y + (h - d) // 2)
    r = d / 2
    yy, xx = np.mgrid[0:d, 0:d]
    a[top:top + d, x:x + d] |= (xx + 0.5 - r) ** 2 + (yy + 0.5 - r) ** 2 <= r * r
    ly = top + (d - letter.shape[0]) // 2
    lx = x + (d - letter.shape[1]) // 2
    hole[ly:ly + letter.shape[0], lx:lx + letter.shape[1]] = letter
    a[hole] = False
    x += d + 3
    b = bang.shape[0]
    a[y + h - b:y + h, x:x + bang.shape[1]] = bang
    return a, hole


def move_paint(canvas, a, luma, hole=None):
    """Colour new letters with one frame's old outline and main fill."""
    used = [i for i in np.unique(canvas).tolist() if i]
    if not used:
        return np.zeros_like(canvas)
    dark = min(used, key=lambda i: luma[i])
    fill = int(np.bincount(canvas[(canvas != 0) & (canvas != dark)], minlength=16).argmax())
    out = np.zeros_like(canvas)
    edge = a.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            edge |= np.roll(np.roll(a, dy, 0), dx, 1)
    shadow = np.roll(np.roll(edge, 1, 0), 1, 1)
    out[edge | shadow] = dark
    out[a] = fill
    if hole is not None:
        out[hole] = 0
    return out


def move_title(rgcn, cells, palette, small, name, twin=None):
    """Redraw every frame of a special move's title, keeping its sprites and colours."""
    pal = np.frombuffer(palette, "<u2", 16, 0x28).astype(int)
    luma = (pal & 31) * 3 + (pal >> 5 & 31) * 6 + (pal >> 10 & 31)
    count, _, at, _, table = struct.unpack_from("<HHIII", cells, 0x18)
    at += 0x18
    oams = at + count * 8
    data = bytearray(rgcn[0x30:])
    extra = bytearray(twin[0x30:]) if twin else None
    for n in range(count):
        parts, off = struct.unpack_from("<H2xI", cells, at + n * 8)
        start = struct.unpack_from("<I", cells, 0x18 + table + 8 + n * 8)[0]
        sprites = []
        for i in range(parts):
            a0, a1, a2 = struct.unpack_from("<3H", cells, oams + off + i * 6)
            sprites.append(((a1 & 0x1FF) - (512 if a1 & 256 else 0), (a0 & 255) - (256 if a0 & 128 else 0),
                            *OBJ_SIZES[a0 >> 14, a1 >> 14], start + (a2 & 1023) * 0x80))
        row = [p for p in sprites if p[3] == 32 and p[1] == next(q[1] for q in sprites if q[2] == 64)]
        for p in sprites:
            if p[3] < 32:
                data[p[4]:p[4] + p[2] * p[3] // 2] = bytes(p[2] * p[3] // 2)
        row.sort()
        width = sum(p[2] for p in row)
        old = np.concatenate([yn_read(data, p[4], p[2], 32, True) for p in row], 1)
        mask, hole = mash_canvas(32, width) if name == "Mash A!" else (move_canvas(32, width, small, name), None)
        new = move_paint(old, mask, luma, hole)
        x = 0
        for p in row:
            part = new[:, x:x + p[2]]
            x += p[2]
            data[p[4]:p[4] + p[2] * 16] = yn_write(part, True)
            if extra is not None:
                extra[p[4]:p[4] + p[2] * 16] = yn_write(part, False)
    return rgcn[:0x30] + bytes(data), (twin[:0x30] + bytes(extra)) if twin else None


def door_label():
    """32x16 "Exit", right aligned so that it sits against the button."""
    letters = plate_text("Exit", 1)
    a = np.zeros((16, 32), dtype=bool)
    x = 30 - letters.shape[1]
    a[3:3 + letters.shape[0], x:x + letters.shape[1]] = letters
    o = a.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            o |= np.roll(np.roll(a, dy, 0), dx, 1)
    px = np.zeros((16, 32), dtype=np.uint8)
    px[o] = 15
    px[a] = 1
    return px


def shop_door(tiles, cells, anim):
    """The exit button: sequence 0 rests dark and bare, sequence 1 pulses with "Exit" beside it."""
    data = tiles[0x30:0x30 + 5 * 0x200]
    label = yn_write(door_label(), True)
    body = b"".join(data[i * 0x200:(i + 1) * 0x200] + label for i in range(5)) + data[4 * 0x200:]
    grown = bytearray(tiles[:0x30]) + body + tiles[0x30 + 5 * 0x200:]
    struct.pack_into("<I", grown, 8, len(grown))
    struct.pack_into("<I", grown, 0x14, 0x20 + len(body))
    struct.pack_into("<I", grown, 0x28, len(body))

    art = cells[0x58:0x5E]
    text = struct.pack("<HHH", 0x40F9, 0x81CC, 4)
    entries = b"".join(struct.pack("<HHI", 2, 0xD, i * 12) for i in range(5)) + struct.pack("<HHI", 1, 6, 60)
    oams = (art + text) * 5 + art + bytes(2)          # the table after it must be word aligned
    table = struct.pack("<II", 0x300, 8)
    table += b"".join(struct.pack("<II", i * 0x300, 0x300) for i in range(5))
    table += struct.pack("<II", 5 * 0x300, 0x200)
    table_at = 0x18 + len(entries) + len(oams)
    section = struct.pack("<HHIII", 6, 0, 0x18, 2, table_at) + bytes(8) + entries + oams + table
    size = struct.unpack_from("<I", cells, 0x14)[0]
    grid = bytearray(cells[:0x10]) + b"KBEC" + struct.pack("<I", 8 + len(section)) + section + cells[0x10 + size:]
    struct.pack_into("<I", grid, 8, len(grid))

    seq = anim[0x30:0x40]
    frames = anim[0x40:0x80]
    rest = bytearray(seq)
    struct.pack_into("<I", rest, 0, 1)
    struct.pack_into("<I", rest, 12, 64)
    frames = frames[32:] + frames[:32] + struct.pack("<IHH", 10, 6, 0xBEEF)
    head = struct.pack("<HHIII", 2, 9, 0x18, 0x38, 0x38 + 72) + bytes(8)
    section = head + bytes(rest) + seq + frames + struct.pack("<6H", 0, 1, 2, 3, 4, 5)
    size = struct.unpack_from("<I", anim, 0x14)[0]
    timing = bytearray(anim[:0x10]) + b"KNBA" + struct.pack("<I", 8 + len(section)) + section + anim[0x10 + size:]
    struct.pack_into("<I", timing, 8, len(timing))
    return bytes(grown), bytes(grid), bytes(timing)


MIX_OLD = 0x680                 # the 13 marker frames
MIX_CELL = 0x700                # 32x32 X, then 32x16 parts of the START and Cancel labels


def mix_x_button():
    """A grey button with an embossed X, in the look of the A prompt."""
    a = np.zeros((32, 32), dtype=np.uint8)
    for (y, x) in np.ndindex(32, 32):
        d = (x - 15.5) ** 2 + (y - 15.5) ** 2
        if d <= 10.6 ** 2:
            a[y, x] = 15
        if d <= 9.6 ** 2:
            a[y, x] = 3
    letter = pixelfont.glyph("X")[:8]
    a[13:21, 14:19][letter] = 14
    a[12:20, 13:18][letter] = 1
    return a


def outlined(a):
    """Index 1 letters with a dark outline."""
    o = a.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            o |= np.roll(np.roll(a, dy, 0), dx, 1)
    px = np.zeros(a.shape, dtype=np.uint8)
    px[o] = 15
    px[a] = 1
    return px


def mix_label():
    """96x16: a grey START button in the X button's style, then its action."""
    text = plate_text("START", 1, 60)[:8]
    w = text.shape[1] + 8
    px = np.zeros((16, 96), dtype=np.uint8)
    px[1:15, 1:1 + w] = 15
    px[1, [1, w]] = px[14, [1, w]] = 0
    px[2:14, 2:w] = 3
    px[4:12, 6:6 + text.shape[1]][text] = 14
    px[3:11, 5:5 + text.shape[1]][text] = 1
    word = plate_text("Combine", 1, 60)
    a = np.zeros((16, 96), dtype=bool)
    a[3:3 + word.shape[0], w + 5:w + 5 + word.shape[1]] = word
    rest = outlined(a)
    px[rest != 0] = rest[rest != 0]
    return px


def mix_cancel():
    """64x16, right aligned against the X button."""
    word = plate_text("Cancel", 1, 60)
    a = np.zeros((16, 64), dtype=bool)
    a[3:3 + word.shape[0], 62 - word.shape[1]:62] = word
    return outlined(a)


def mix_frame(rgcn, tiled):
    """Add the prompts after the marker's 13 frames, which stay as they are."""
    button, label, cancel = mix_x_button(), mix_label(), mix_cancel()
    extra = yn_write(button, tiled) + b"".join(yn_write(label[:, x:x + 32], tiled) for x in (0, 32, 64))
    extra += b"".join(yn_write(cancel[:, x:x + 32], tiled) for x in (0, 32))
    end = 0x30 + MIX_OLD
    body = rgcn[0x30:end] + extra
    out = bytearray(rgcn[:0x30]) + body + rgcn[end:]
    struct.pack_into("<I", out, 8, len(out))
    struct.pack_into("<I", out, 0x14, 0x20 + len(body))
    struct.pack_into("<I", out, 0x28, len(body))
    return bytes(out)


def mix_prompts(tiles, bitmap, cells, anim):
    """These files are also the field's marker over things to use, so sequence 0 is untouched.

    Sequence 1 is one new cell, which only the mixing room selects.
    """
    n, _, at, _, table = struct.unpack_from("<HHIII", cells, 0x18)
    at += 0x18
    oams = at + n * 8
    table += 0x18
    sprites = cells[oams:oams + n * 6]
    new = struct.pack("<HHH", 0x00A6, 0x8000 | 38, 0)
    for i, x in enumerate((-52, -20, 12)):
        new += struct.pack("<HHH", 0x4000 | 56, 0x8000 | x & 0x1FF, 4 + i * 2)
    for i, x in enumerate((-24, 8)):
        new += struct.pack("<HHH", 0x40AE, 0x8000 | x & 0x1FF, 10 + i * 2)
    entries = cells[at:oams] + struct.pack("<HHI", 6, 0x1F, len(sprites))
    sprites += new
    sprites += bytes(-len(sprites) % 4)
    frames = cells[table + 8:table + 8 + n * 8] + struct.pack("<II", MIX_OLD, MIX_CELL)
    head = struct.pack("<HHIII", n + 1, 0, 0x18, 2, 0x18 + len(entries) + len(sprites)) + bytes(8)
    section = head + entries + sprites + struct.pack("<II", MIX_CELL, 8) + frames
    size = struct.unpack_from("<I", cells, 0x14)[0]
    grid = bytearray(cells[:0x10]) + b"KBEC" + struct.pack("<I", 8 + len(section)) + section + cells[0x10 + size:]
    struct.pack_into("<I", grid, 8, len(grid))

    seq = anim[0x30:0x40]
    frames = anim[0x40:0xA8]
    data = anim[0xA8:0xC2]
    rest = bytearray(seq)
    struct.pack_into("<I", rest, 0, 1)
    struct.pack_into("<I", rest, 12, len(frames))
    frames += struct.pack("<IHH", len(data), 2, 0xBEEF)
    head = struct.pack("<HHIII", 2, 14, 0x18, 0x38, 0x38 + len(frames)) + bytes(8)
    body = head + seq + bytes(rest) + frames + data + struct.pack("<H", 13)
    body += bytes(-len(body) % 4)
    size = struct.unpack_from("<I", anim, 0x14)[0]
    timing = bytearray(anim[:0x10]) + b"KNBA" + struct.pack("<I", 8 + len(body)) + body + anim[0x10 + size:]
    struct.pack_into("<I", timing, 8, len(timing))
    return mix_frame(tiles, True), mix_frame(bitmap, False), bytes(grid), bytes(timing)


def mix_page(screen):
    """Paint out the X card with a mirror image of the rows below it."""
    grid = bytearray(screen)
    for y in range(3):
        for x in range(29, 32):
            entry = struct.unpack_from("<H", screen, 0x24 + ((5 - y) * 32 + x) * 2)[0]
            struct.pack_into("<H", grid, 0x24 + (y * 32 + x) * 2, entry ^ 0x800)
    return bytes(grid)


MIX_LETTERS = {"R": ("##.", "#.#", "##.", "#.#", "#.#"), "L": ("#..", "#..", "#..", "#..", "###")}


def mix_badge(letter):
    """9x9 shoulder button: 0 clear, 1 outline, 2 face, 3 letter."""
    a = np.full((9, 9), 2, dtype=np.uint8)
    a[0] = a[-1] = 1
    a[:, 0] = a[:, -1] = 1
    for y in (0, -1):
        a[y, [0, -1]] = 0
    for y, row in enumerate(MIX_LETTERS[letter]):
        for x, c in enumerate(row):
            if c == "#":
                a[2 + y, 3 + x] = 3
    return a


def mix_switch():
    """The tab prompt, 20x18: L and R side by side, each above its arrow."""
    a = np.zeros((18, 20), dtype=np.uint8)
    a[0:9, 0:9] = mix_badge("L")
    a[0:9, 11:20] = mix_badge("R")
    fill = np.zeros((9, 6), dtype=bool)
    for i in range(4):
        fill[4 - i:5 + i, 1 + i] = True
    edge = np.pad(fill, 1)
    near = edge.copy()
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        near |= np.roll(np.roll(edge, dy, 0), dx, 1)
    arrow = np.where(edge, 3, np.where(near, 1, 0)).astype(np.uint8)[1:-1, :]
    h, w = arrow.shape
    a[18 - h:, 2:2 + w] = arrow[:, :]
    a[18 - h:, 18 - w:18] = arrow[:, ::-1]
    return a


ITEM_BADGE = ("..ffffff..",
              ".f111111f.",
              "f11ff1111f",
              "f11ff1111f",
              "f11ff1111f",
              "f11ff1111f",
              "f11ffff11f",
              "f11ffff11f",
              ".f111111f.",
              "..ffffff..")
ITEM_BADGE_X, ITEM_BADGE_Y = -11, 28    # hangs off the item square's bottom right corner


def item_badge(tiles, cells):
    """Give the item square (files 5316, 5315) a small L button as its own sprite, in front of the square."""
    art = bytearray(128)
    for y, row in enumerate(ITEM_BADGE):
        for x, c in enumerate(row):
            if c != ".":
                i = ((y // 8) * 2 + x // 8) * 64 + (y % 8) * 8 + x % 8
                art[i // 2] |= int(c, 16) << (4 if i & 1 else 0)
    out = bytearray(tiles) + art
    struct.pack_into("<I", out, 8, len(out))
    struct.pack_into("<I", out, 0x14, struct.unpack_from("<I", out, 0x14)[0] + len(art))
    struct.pack_into("<I", out, 0x28, struct.unpack_from("<I", out, 0x28)[0] + len(art))
    grid = bytearray(cells)
    square = grid[0x38:0x3E]
    badge = struct.pack("<HHH", ITEM_BADGE_Y & 0xFF, 0x4000 | ITEM_BADGE_X & 0x1FF, 4)     # tiles count in 128 bytes
    grid[0x38:0x40] = badge + bytes(square) + bytes(4)
    struct.pack_into("<H", grid, 0x30, 2)
    assert struct.unpack_from("<I", grid, 0x48)[0] == 0x200
    struct.pack_into("<I", grid, 0x48, 0x280)
    struct.pack_into("<I", grid, 0x54, 0x280)
    struct.pack_into("<I", grid, 8, len(grid))
    struct.pack_into("<I", grid, 0x14, 0x48)
    struct.pack_into("<I", grid, 0x24, 0x30)
    return bytes(out), bytes(grid)


def smith_rows(rgcn):
    """Dim the orange borders of the smith's material rows: the selection ring is the orange one."""
    out = bytearray(rgcn)
    swap = {11: 3, 12: 14}
    for i in range(0x30, len(out)):
        lo, hi = out[i] & 15, out[i] >> 4
        out[i] = swap.get(lo, lo) | swap.get(hi, hi) << 4
    return bytes(out)


WEAPON_LABELS = (("Time Left", 28), ("Weapon Effect", 88))


def weapon_effect(rgcn, cells):
    """The equip screen's weapon effect strip, file 5592: 256x32 in 64x32 sprites.

    The file held the strip twice, the second copy for the frame that hides the colon, and
    other graphics overwrote the end of that copy. Both frames now share one strip. The
    frame that hides the colon covers it with two 8x8 sprites that reuse the strip's own
    dark box tiles, so nothing reaches past the strip's 4 KB of sprite memory."""
    out = bytearray(rgcn[:0x30 + 0x1000])
    cover = rgcn[0x30 + 0x1000:0x30 + 0x1040]

    def pixel(x, y):
        tile = (x // 64) * 32 + (y // 8) * 8 + (x % 64) // 8
        i = tile * 64 + (y % 8) * 8 + x % 8
        return 0x30 + i // 2, i & 1

    for y in range(1, 17):
        for x in range(24, 170):
            o, hi = pixel(x, y)
            out[o] &= 0x0F if hi else 0xF0
    for text, left in WEAPON_LABELS:
        a = outlined(np.pad(plate_text(text, 1, 110), 1))
        for y, row in enumerate(a):
            for x, v in enumerate(row):
                if v:
                    o, hi = pixel(left + x, 2 + y)
                    c = 9 if v == 1 else 15
                    out[o] = (out[o] & 0x0F) | c << 4 if hi else (out[o] & 0xF0) | c
    top, bottom = 20, 28                                 # strip tiles equal to the cover's two
    assert out[0x30 + top * 32:0x30 + top * 32 + 32] == cover[:32]
    assert out[0x30 + bottom * 32:0x30 + bottom * 32 + 32] == cover[32:]
    struct.pack_into("<I", out, 8, len(out))
    struct.pack_into("<I", out, 0x14, 0x20 + 0x1000)
    struct.pack_into("<I", out, 0x28, 0x1000)
    assert struct.unpack_from("<HHI", cells, 0x38) == (5, 0x34, 0x18)
    assert struct.unpack_from("<3H", cells, 0x58) == (0x80F8, 0x01FC, 0)
    assert struct.unpack_from("<6I", cells, 0x78) == (0x1080, 8, 0, 0x1000, 0x1000, 0x1080)
    oam = bytearray(cells[0x40:0x58])
    oam += struct.pack("<3H", 0x00F8, 0x01FC, top // 4)   # 8x8 each, in 128-byte units
    oam += struct.pack("<3H", 0x0000, 0x01FC, bottom // 4)
    for n in range(4):
        oam += cells[0x5E + n * 6:0x5E + n * 6 + 4] + struct.pack("<H", n * 8)
    grid = bytearray(cells[:0x40]) + oam                  # ends at 0x7C
    grid += struct.pack("<6I", 0x1000, 8, 0, 0x1000, 0, 0x1000)
    struct.pack_into("<HHI", grid, 0x38, 6, 0x34, 0x18)
    assert struct.unpack_from("<I", grid, 0x24)[0] == 0x60
    struct.pack_into("<I", grid, 0x24, 0x7C - 0x18)      # where the transfer list starts
    struct.pack_into("<I", grid, 0x14, len(grid) - 0x10)
    grid += cells[0x90:]
    struct.pack_into("<I", grid, 8, len(grid))
    return bytes(out), bytes(grid)


GLOW_FREE = {1: 2, 7: 6, 13: 12, 5: 4}   # near-duplicate whites whose slots the outline takes
GLOW_SLOTS = (1, 7, 13, 5)
GLOW_SHADES = ((24, 72, 176), (40, 104, 224), (80, 144, 248), (136, 192, 248))   # dim to bright
GLOW_CYCLE = (0, 1, 2, 3, 2, 1)          # the outline's frames, 6 ticks each
GLOW_RECT = 21, 5, 170, 29, 11           # the button's rounded edge: left, top, right, bottom, radius


def title_glow(chars, cells, anim, pal):
    """The title menu buttons, files 5384 (chars), 5385 (cells), 5383 (anims), 5386 (palette).

    The button is a 192x32 linear bitmap in three 64x32 sprites: normal, then pressed. Four more
    copies of the normal one get a solid blue outline along its rounded edge, one per shade, and
    sequence 2 cycles them so the selected button's outline pulses."""
    data = bytearray(chars[0x30:0x30 + 0x1800])
    for i, v in enumerate(data):
        lo, hi = GLOW_FREE.get(v & 15, v & 15), GLOW_FREE.get(v >> 4, v >> 4)
        data[i] = lo | hi << 4
    x0, y0, x1, y1, r = GLOW_RECT
    ring = []
    for y in range(32):
        for x in range(192):
            dx = max(x0 + r - x, 0, x - (x1 - r))
            dy = max(y0 + r - y, 0, y - (y1 - r))
            if -1 < (dx * dx + dy * dy) ** 0.5 - r <= 1:
                ring.append(((x // 64) * 0x400 + (y * 64 + x % 64) // 2, x & 1))
    out = bytearray(chars[:0x30]) + data
    for c in GLOW_SLOTS:
        img = bytearray(data[:0xC00])
        for o, hi in ring:
            img[o] = (img[o] & 0x0F) | c << 4 if hi else (img[o] & 0xF0) | c
        out += img
    struct.pack_into("<I", out, 8, len(out))
    struct.pack_into("<I", out, 0x14, len(out) - 0x10)
    struct.pack_into("<I", out, 0x28, len(out) - 0x30)

    p = bytearray(pal)
    for k, (cr, cg, cb) in zip(GLOW_SLOTS, GLOW_SHADES):
        struct.pack_into("<H", p, 0x28 + k * 2, cr >> 3 | (cg >> 3) << 5 | (cb >> 3) << 10)

    g = bytes(cells)
    assert struct.unpack_from("<HHI", g, 0x18) == (2, 0, 0x18)
    assert struct.unpack_from("<6I", g, 0x64) == (0xC00, 8, 0, 0xC00, 0xC00, 0xC00)
    n = 2 + len(GLOW_SLOTS)
    cell_tab = g[0x30:0x40] + b"".join(struct.pack("<HHI", 3, 0x19, 36 + 18 * k) for k in range(len(GLOW_SLOTS)))
    oam = g[0x40:0x64] + g[0x40:0x52] * len(GLOW_SLOTS)   # the new cells: the normal layout
    grid = bytearray(g[:0x30]) + cell_tab + oam
    grid += bytes(-len(grid) % 4)
    xfer = len(grid)
    grid += struct.pack("<2I", 0xC00, 8) + b"".join(struct.pack("<2I", k * 0xC00, 0xC00) for k in range(n))
    struct.pack_into("<HHI", grid, 0x18, n, 0, 0x18)
    struct.pack_into("<I", grid, 0x24, xfer - 0x18)
    struct.pack_into("<I", grid, 0x14, len(grid) - 0x10)
    grid += g[0x7C:]
    struct.pack_into("<I", grid, 8, len(grid))

    a = bytes(anim)
    assert struct.unpack_from("<HHIII", a, 0x18) == (2, 2, 0x18, 0x38, 0x48)
    seqs = a[0x30:0x50] + struct.pack("<HHIII", len(GLOW_CYCLE), 0, 0x10000, 2, 16)
    frames = a[0x50:0x60] + b"".join(struct.pack("<IHH", 8 + 4 * k, 6, 0xBEEF) for k in range(len(GLOW_CYCLE)))
    cellref = a[0x60:0x68] + b"".join(struct.pack("<HH", 2 + k, 0xCCCC) for k in GLOW_CYCLE)
    na = bytearray(a[:0x30]) + seqs
    fo = len(na) - 0x18
    na += frames
    do = len(na) - 0x18
    na += cellref
    struct.pack_into("<HHIII", na, 0x18, 3, 2 + len(GLOW_CYCLE), 0x18, fo, do)
    struct.pack_into("<I", na, 0x14, len(na) - 0x10)
    na += a[0x68:]
    struct.pack_into("<I", na, 8, len(na))
    return bytes(out), bytes(grid), bytes(na), bytes(p)


def menu_board(cells):
    """Centre the bag board's cell on x 0, so that stretching it keeps it on screen."""
    out = bytearray(cells)
    for i in range(6):
        at = 0x3A + i * 6
        a1 = struct.unpack_from("<H", out, at)[0]
        x = ((a1 & 0x1FF) - 128) & 0x1FF
        struct.pack_into("<H", out, at, a1 & ~0x1FF | x)
    return bytes(out)


SHOP_YN_CELL = 0x580            # 32x16 label, then a 48x48 portrait in four sprites
SHOP_YN_PARTS = (0x100, 32, 32, 0, 0), (0x300, 16, 32, 32, 0), (0x400, 32, 16, 0, 32), (0x500, 16, 16, 32, 32)


def shop_yn_frame(rgcn, o, tiled, lit):
    """One frame with the two freed shades merged; with lit, a bright rim and the arrows."""
    out = bytearray(rgcn[o:o + SHOP_YN_CELL])
    art = np.zeros((48, 48), dtype=np.uint8)
    for off, w, h, x, y in SHOP_YN_PARTS:
        art[y:y + h, x:x + w] = yn_read(rgcn, o + off, w, h, tiled)
    label = yn_read(rgcn, o, 32, 16, tiled)
    for im in (label, art):
        im[im == YN_BROWN] = 15
        im[im == YN_BLUE] = 3
    if lit:
        ring = np.ones((48, 48), dtype=bool)
        ring[3:45, 3:45] = False
        was = art.copy()
        art[ring & (was == 9)] = YN_BLUE
        art[ring & (was == 4)] = YN_BROWN
    out[:0x100] = yn_write(label, tiled)
    for off, w, h, x, y in SHOP_YN_PARTS:
        part = yn_write(art[y:y + h, x:x + w], tiled)
        out[off:off + len(part)] = part
    if lit:
        out += yn_write(yn_arrow(True), tiled) + yn_write(yn_arrow(False), tiled)
    return bytes(out)


def shop_yn_grow(rgcn, tiled):
    data = rgcn[0x30:]
    base = b"".join(shop_yn_frame(data, i * SHOP_YN_CELL, tiled, False) for i in range(4))
    lit = b"".join(shop_yn_frame(data, i * SHOP_YN_CELL, tiled, True) for i in range(4))
    body = base + lit
    out = bytearray(rgcn[:0x30]) + body + data[4 * SHOP_YN_CELL:]
    struct.pack_into("<I", out, 8, len(out))
    struct.pack_into("<I", out, 0x14, 0x20 + len(body))
    struct.pack_into("<I", out, 0x28, len(body))
    return bytes(out)


def shop_yes_no(tiles, bitmap, cells, anim):
    """The shop's smaller Yes and No cards: sequences 2 and 3 are the selected ones."""
    new_size = SHOP_YN_CELL + YN_ARROWS
    old = cells[0x50:0x50 + 30 * 4]
    card = old[:30]
    left = struct.pack("<HHH", 0x00D8, 0x41E7, 0xB)
    right = struct.pack("<HHH", 0x00D8, 0x400A, 0xC)
    entries = cells[0x30:0x50] + b"".join(struct.pack("<HHI", 7, 0xD, 120 + i * 42) for i in range(4))
    oams = old + (card + left + right) * 4
    table_at = 0x18 + len(entries) + len(oams)
    table = struct.pack("<II", new_size, 8)
    table += b"".join(struct.pack("<II", i * SHOP_YN_CELL, SHOP_YN_CELL) for i in range(4))
    table += b"".join(struct.pack("<II", 4 * SHOP_YN_CELL + i * new_size, new_size) for i in range(4))
    head = struct.pack("<HHIII", 8, 0, 0x18, 2, table_at) + bytes(8)
    section = head + entries + oams + table
    size = struct.unpack_from("<I", cells, 0x14)[0]
    grid = bytearray(cells[:0x10]) + b"KBEC" + struct.pack("<I", 8 + len(section)) + section + cells[0x10 + size:]
    struct.pack_into("<I", grid, 8, len(grid))

    seqs = anim[0x30:0x50]
    frames = anim[0x50:0x70]
    seq2 = bytearray(seqs[:16])
    struct.pack_into("<I", seq2, 12, 0x20)
    seq3 = bytearray(seqs[:16])
    struct.pack_into("<I", seq3, 12, 0x30)
    more = b"".join(struct.pack("<IHH", off, dur, 0xBEEF) for off, dur in ((8, 20), (10, 10), (12, 15), (14, 15)))
    head = struct.pack("<HHIII", 4, 8, 0x18, 0x58, 0x98) + bytes(8)
    data = anim[0x70:0x78] + struct.pack("<4H", 4, 5, 6, 7)
    section = head + seqs + bytes(seq2) + bytes(seq3) + frames + more + data
    timing = bytearray(anim[:0x10]) + b"KNBA" + struct.pack("<I", 8 + len(section)) + section + anim[0x78:]
    struct.pack_into("<I", timing, 8, len(timing))
    return shop_yn_grow(tiles, True), shop_yn_grow(bitmap, False), bytes(grid), bytes(timing)


NAME_PLATES = """Lief|Barda|Jasmine|Doom|Dain|Jarred|Anna|Fallow|Prandine|Sharn|Crian|Mother Brightly|Manus|Glock
Zeean|Fardeep|Queen Bee|Tira|Prin|Crenn|Kin|Fa-Glin|Gla-Thon|Steven|Jack|Mokeet|Mikeeta|Endon|???|Gorl|Soldeen
Thaegan|Reeah|Gellick|Ra-Kacharz|Ra-Kacharz|Mary|Ida|Jin|Jod|Nij|Doj|Ferdinand|Captain|Spirit""".replace("\n", "|").split("|")
PLATE_BASE = 4534


def plate_text(text, gap, room=62):
    """The dialogue font's letters in one row, or None if they don't fit the plate."""
    parts = [(None if c == " " else pixelfont.glyph(c)) for c in text]
    w = sum(3 if p is None else p.shape[1] + gap for p in parts) - gap
    if w > room:
        return None
    a = np.zeros((pixelfont.CAP + 2, w), dtype=bool)
    x = 0
    for p in parts:
        if p is None:
            x += 3
            continue
        a[:, x:x + p.shape[1]] = p
        x += p.shape[1] + gap
    return a


def narrow(g, least=5):
    """A letter at least `least` wide with one inner column dropped, the one most like its neighbour."""
    if g.shape[1] < least:
        return g
    k = min(range(1, g.shape[1] - 1), key=lambda c: (g[:, c] != g[:, c + 1]).sum())
    return np.delete(g, k, 1)


THINNEST = "oher"   # 3 wide in a condensed plate: the frame hides 3 pixels at the plate's outer side
CONDENSED_X = 4     # where a condensed name starts: clear of the right plate's frame, and the left plate's


def condensed(text):
    """The dialogue font's letters made narrow (M and W keep their diagonals), spaced only
    where two letters would meet on a row."""
    rows = []
    for c in text:
        if c == " ":
            rows.append(np.zeros((pixelfont.CAP + 2, 2), dtype=bool))
            continue
        g = pixelfont.glyph(c) if c in "MW" else narrow(pixelfont.glyph(c))
        if c in THINNEST:
            g = np.delete(g, 1, 1)
        if c == "t":
            g = narrow(g, 4)    # keeps the stem: drops the crossbar's doubled right column
        if rows and (rows[-1][:, -1] & g[:, 0]).any():
            rows.append(np.zeros((g.shape[0], 1), dtype=bool))
        rows.append(g)
    return np.hstack(rows)


def name_plate(text):
    """64x16 plate as two 32x16 sprites. Index 1 is brightest in this palette."""
    W, H = 64, 16
    letters = plate_text(text, 1)
    letters = plate_text(text, 0) if letters is None else letters
    px = np.zeros((H, W), dtype=np.uint8)
    if letters is not None:
        x = (W - letters.shape[1]) // 2
        px[3:3 + letters.shape[0], x:x + letters.shape[1]][letters] = 1
    else:
        letters = condensed(text)
        assert letters.shape[1] <= W - 6, (text, letters.shape)       # the left plate loses its right 3 pixels, the right plate its left 3
        x = CONDENSED_X
        px[3:3 + letters.shape[0], x:x + letters.shape[1]][letters] = 1
    out = bytearray(512)
    n = 0
    for sprite in range(2):
        for ty in range(2):
            for tx in range(4):
                for y in range(8):
                    for x in range(0, 8, 2):
                        X = sprite * 32 + tx * 8 + x
                        Y = ty * 8 + y
                        out[n] = int(px[Y, X]) | int(px[Y, X + 1]) << 4
                        n += 1
    return bytes(out)


def patch_name_plate(rgcn, text):
    b = bytearray(rgcn)
    b[0x30:0x30 + 512] = name_plate(text)
    return bytes(b)


def patch_bar(rgcn, rlcn, rcsn, box, text, size=12):
    """Swap bright text on a dark bar. box = (x0, y0, x1, y1) around the text."""
    n = struct.unpack_from("<I", rlcn, 0x20)[0]
    c = struct.unpack_from(f"<{n // 2}H", rlcn, 0x28)
    p = np.array([[(x & 31) * 255 / 31, (x >> 5 & 31) * 255 / 31, (x >> 10 & 31) * 255 / 31] for x in c], dtype=np.float32)
    b = bytearray(rgcn)
    s = bytearray(rcsn)
    m = list(struct.unpack_from("<1024H", s, 0x24))
    rgb = np.zeros((192, 256, 3), dtype=np.float32)
    for r in range(24):
        for k in range(32):
            e = m[r * 32 + k]
            o = 0x30 + (e & 0x3FF) * 32
            for y in range(8):
                for x in range(8):
                    by = b[o + y * 4 + x // 2]
                    rgb[r * 8 + y, k * 8 + x] = p[(e >> 12) * 16 + (by >> 4 if x & 1 else by & 15)]
    x0, y0, x1, y1 = box
    lum = rgb.mean(2)
    mask = np.zeros((192, 256), dtype=bool)
    mask[y0:y1, x0:x1] = lum[y0:y1, x0:x1] > 90
    grown = mask | np.roll(mask, 1, 0) | np.roll(mask, -1, 0) | np.roll(mask, 1, 1) | np.roll(mask, -1, 1)
    mask = grown
    mask[:y0], mask[y1:] = False, False
    mask[:, :x0], mask[:, x1:] = False, False
    # fill old text from the bar colour around it
    known = ~mask
    out = rgb.copy()
    while not known.all():
        acc = np.zeros_like(out)
        cnt = np.zeros((192, 256), dtype=np.float32)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            acc += np.roll(np.roll(out * known[..., None], dy, 0), dx, 1)
            cnt += np.roll(np.roll(known, dy, 0), dx, 1)
        g = ~known & (cnt > 0)
        out[g] = acc[g] / cnt[g][..., None]
        known |= g
    hi = Image.new("L", (256 * SS, 192 * SS))
    f = ImageFont.truetype(BOLD, size * SS)
    ImageDraw.Draw(hi).text(((x0 + x1) * SS // 2, (y0 + y1) * SS // 2), text, fill=255, font=f, anchor="mm")
    a = np.asarray(hi.resize((256, 192), Image.LANCZOS), dtype=np.float32) / 255
    out = out * (1 - a[..., None]) + np.array((246, 246, 240), dtype=np.float32) * a[..., None]
    change = mask | (a > 0.05)
    # recolour changed pixels only, inside each tile's existing palette
    for r in range(y0 // 8, (y1 + 7) // 8):
        for k in range(x0 // 8, (x1 + 7) // 8):
            e = m[r * 32 + k]
            cols = p[(e >> 12) * 16 + 1:(e >> 12) * 16 + 16]
            o = 0x30 + (e & 0x3FF) * 32
            for y in range(8):
                for x in range(8):
                    Y, X = r * 8 + y, k * 8 + x
                    if not change[Y, X]:
                        continue
                    v = int(((cols - out[Y, X]) ** 2).sum(1).argmin()) + 1
                    q = o + y * 4 + x // 2
                    b[q] = (b[q] & 0x0F) | v << 4 if x & 1 else (b[q] & 0xF0) | v
    return bytes(b), bytes(s)


def patch_save_sign(rgcn):
    """File 5411: four 32x32 frames, stored as one linear 4bpp bitmap."""
    b = bytearray(rgcn)
    d = np.zeros((128, 32), dtype=np.uint8)
    for i in range(32 * 128):
        by = b[0x30 + i // 2]
        d[i // 32, i % 32] = by >> 4 if i & 1 else by & 15
    letters = (
        ["####", "#   ", "#   ", "####", "   #", "   #", "####"],
        ["    ", "    ", "### ", "   #", "####", "#  #", "####"],
        ["    ", "    ", "#  #", "#  #", "#  #", " ## ", " ## "],
        ["    ", "    ", "####", "#  #", "####", "#   ", "####"],
    )
    a = np.zeros((16, 32), dtype=bool)
    for i, g in enumerate(letters):
        for y, row in enumerate(g):
            for x, c in enumerate(row):
                a[y + 5, x + 7 + i * 5] = c == "#"
    o = a.copy()
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        o |= np.roll(np.roll(a, dy, 0), dx, 1)
    for fr in range(4):
        top = fr * 32 + 10
        old = d[top:top + 15, 5:27].copy()
        text = (old == 5) | (old == 1) | (old == 2) | (old == 3)
        known = ~text
        # patch the parchment, then letter over it
        while not known.all():
            for y in range(15):
                for x in range(22):
                    if known[y, x]:
                        continue
                    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        Y, X = y + dy, x + dx
                        if 0 <= Y < 15 and 0 <= X < 22 and known[Y, X]:
                            old[y, x] = old[Y, X]
                            known[y, x] = True
                            break
        d[top:top + 15, 5:27] = old
        region = d[fr * 32 + 9:fr * 32 + 25]
        region[o] = 1
        region[a] = 5
    for i in range(32 * 128):
        v = int(d[i // 32, i % 32])
        q = 0x30 + i // 2
        b[q] = (b[q] & 0x0F) | v << 4 if i & 1 else (b[q] & 0xF0) | v
    return bytes(b)


def _row_major(tiles):
    """32x16 sprite: 1D tile order to row-major bitmap order."""
    out = bytearray(256)
    for ty in range(2):
        for tx in range(4):
            for y in range(8):
                src = (ty * 4 + tx) * 32 + y * 4
                out[(ty * 8 + y) * 16 + tx * 4:(ty * 8 + y) * 16 + tx * 4 + 4] = tiles[src:src + 4]
    return bytes(out)


def patch_bitmap_labels(rgcn, table):
    """Replace 32x16 labels in a linear twin. table: original tiles -> new tiles.

    Animation frames sit at varying offsets, so scan the whole file.
    Returns the new file and the number of labels replaced.
    """
    b = bytearray(rgcn)
    n = 0
    for old, new in table.items():
        old, new = _row_major(old), _row_major(new)
        o = b.find(old)
        while o >= 0:
            b[o:o + 256] = new
            n += 1
            o = b.find(old, o + 256)
    return bytes(b), n


def patch_copyright(rgcn, rlcn, rcsn, text, box):
    """Redraw one line of small ink text on the plain paper of the title logo."""
    n = struct.unpack_from("<I", rlcn, 0x20)[0]
    c = struct.unpack_from(f"<{n // 2}H", rlcn, 0x28)
    p = np.array([[(x & 31) * 255 / 31, (x >> 5 & 31) * 255 / 31, (x >> 10 & 31) * 255 / 31] for x in c], dtype=np.float32)
    b = bytearray(rgcn)
    s = bytearray(rcsn)
    m = list(struct.unpack_from("<1024H", s, 0x24))
    rgb = np.zeros((192, 256, 3), dtype=np.float32)
    for r in range(24):
        for k in range(32):
            e = m[r * 32 + k]
            o = 0x30 + (e & 0x3FF) * 32
            for y in range(8):
                for x in range(8):
                    by = b[o + y * 4 + x // 2]
                    rgb[r * 8 + y, k * 8 + x] = p[(e >> 12) * 16 + (by >> 4 if x & 1 else by & 15)]
    x0, y0, x1, y1 = box
    ink = rgb[y0:y1, x0:x1].reshape(-1, 3)
    ink = ink[ink.sum(1).argmin()]
    paper = rgb[y0 - 3, x0 - 4].copy()
    out = rgb.copy()
    out[y0:y1, x0:x1] = paper
    size = 9
    f = ImageFont.truetype(NARROW, size * 8)
    hi = Image.new("L", (256 * 8, 192 * 8))
    ImageDraw.Draw(hi).text(((x0 + x1) * 4, (y0 + y1) * 4), text, fill=255, font=f, anchor="mm")
    assert f.getlength(text) / 8 <= x1 - x0, f.getlength(text) / 8
    a = np.asarray(hi.resize((256, 192), Image.LANCZOS), dtype=np.float32) / 255
    a = np.clip(a * 1.5, 0, 1)
    out = out * (1 - a[..., None]) + ink * a[..., None]
    for r in range(y0 // 8, (y1 + 7) // 8):
        for k in range(x0 // 8, (x1 + 7) // 8):
            t = out[r * 8:r * 8 + 8, k * 8:k * 8 + 8].reshape(64, 3)
            if np.abs(t - rgb[r * 8:r * 8 + 8, k * 8:k * 8 + 8].reshape(64, 3)).sum() == 0:
                continue
            best = None
            for pb in range(16):
                d = ((t[:, None, :] - p[pb * 16 + 1:pb * 16 + 16][None]) ** 2).sum(2)
                sc = d.min(1).sum()
                if best is None or sc < best:
                    best, idx, bp = sc, d.argmin(1) + 1, pb
            e = m[r * 32 + k]
            o = 0x30 + (e & 0x3FF) * 32
            for i in range(64):
                y, x = i // 8, i % 8
                q = o + y * 4 + x // 2
                b[q] = (b[q] & 0x0F) | int(idx[i]) << 4 if x & 1 else (b[q] & 0xF0) | int(idx[i])
            m[r * 32 + k] = (e & 0x0FFF) | bp << 12
    struct.pack_into("<1024H", s, 0x24, *m)
    return bytes(b), bytes(s)
