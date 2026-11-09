"""Redraw the title logo subtitle as 'The 7 Gems' in the original fiery style."""
import paths
import struct

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT = paths.font("georgiab.ttf")
TEXT = "The 7 Gems"
PAPER = (255, 255, 246)
BOX = (84, 102, 172, 120)    # x0, y0, x1, y1 cleared on the title bitmap
SIZE = 13
SS = 6


def _pal(b):
    n = struct.unpack_from("<I", b, 0x20)[0]
    c = struct.unpack_from(f"<{n // 2}H", b, 0x28)
    return np.array([[(x & 31) * 255 // 31, (x >> 5 & 31) * 255 // 31, (x >> 10 & 31) * 255 // 31] for x in c], dtype=np.float32)


def lettering():
    """RGBA lettering: fire gradient, dark outline, grey drop shadow."""
    font = ImageFont.truetype(FONT, SIZE * SS)
    w = int(font.getlength(TEXT)) + 8 * SS
    hi = Image.new("L", (w, 26 * SS))
    ImageDraw.Draw(hi).text((4 * SS, 2 * SS), TEXT, fill=255, font=font)
    sz = (w // SS, 26)
    fill = np.asarray(hi.resize(sz, Image.LANCZOS), dtype=np.float32) / 255
    rows = np.where(fill.max(1) > 0.3)[0]
    cols = np.where(fill.max(0) > 0.3)[0]
    top, bot = rows[0], rows[-1]
    outline = np.asarray(hi.filter(ImageFilter.MaxFilter(SS * 2 + 1)).resize(sz, Image.LANCZOS), dtype=np.float32) / 255
    h, wd = fill.shape
    rgb = np.zeros((h, wd, 3), dtype=np.float32)
    stops = [(0.0, (160, 40, 10)), (0.25, (232, 84, 16)), (0.5, (250, 168, 28)), (0.72, (255, 224, 64)), (1.0, (255, 244, 130))]
    for y in range(h):
        t = np.clip((y - top) / max(1, bot - top), 0, 1)
        for (a, ca), (b, cb) in zip(stops, stops[1:]):
            if t <= b:
                f = (t - a) / (b - a)
                rgb[y, :] = np.array(ca) * (1 - f) + np.array(cb) * f
                break
    return rgb, fill, outline, cols[0], cols[-1], top


def compose(bg, box=BOX, centre=128, top_y=103, paper=True):
    """bg: float RGB array of the screen. Returns the edited array."""
    out = bg.copy()
    x0, y0, x1, y1 = box
    if paper:
        out[y0:y1, x0:x1] = PAPER
    else:
        # textured background: blend each row across from its clean edges
        rng = np.random.default_rng(7)
        for y in range(y0, y1):
            left = bg[y, x0 - 4:x0].mean(0)
            right = bg[y, x1:x1 + 4].mean(0)
            t = np.linspace(0, 1, x1 - x0)[:, None]
            out[y, x0:x1] = left * (1 - t) + right * t + rng.normal(0, 3, (x1 - x0, 1))
    rgb, fill, outline, cl, cr, top = lettering()
    ox = centre - (cl + cr) // 2
    oy = top_y - top
    h, w = fill.shape
    for dx, dy, col, alpha in ((1, 1, (123, 148, 139), outline), (0, 0, (32, 24, 16), outline)):
        for y in range(h):
            for x in range(w):
                a = alpha[y, x]
                if a > 0.15:
                    X, Y = x + ox + dx, y + oy + dy
                    out[Y, X] = out[Y, X] * (1 - a) + np.array(col, dtype=np.float32) * a
    for y in range(h):
        for x in range(w):
            a = fill[y, x]
            if a > 0.1:
                out[y + oy, x + ox] = out[y + oy, x + ox] * (1 - a) + rgb[y, x] * a
    return out


def patch(rgcn, rlcn, rcsn, box=BOX, centre=128, top_y=103, paper=True):
    """Return (rgcn, rcsn) with the subtitle replaced."""
    p = _pal(rlcn)
    b = bytearray(rgcn)
    s = bytearray(rcsn)
    m = list(struct.unpack_from("<1024H", s, 0x24))
    rgb = np.zeros((192, 256, 3), dtype=np.float32)
    for r in range(24):
        for c in range(32):
            e = m[r * 32 + c]
            o = 0x30 + (e & 0x3FF) * 32
            for y in range(8):
                for x in range(8):
                    by = b[o + y * 4 + x // 2]
                    v = by >> 4 if x & 1 else by & 15
                    rgb[r * 8 + y, c * 8 + x] = p[(e >> 12) * 16 + v]
    new = compose(rgb, box, centre, top_y, paper)
    x0, y0, x1, y1 = box
    for r in range(y0 // 8, min(23, (y1 + 8) // 8) + 1):
        for c in range(x0 // 8, x1 // 8 + 1):
            t = new[r * 8:r * 8 + 8, c * 8:c * 8 + 8].reshape(64, 3)
            if np.abs(t - rgb[r * 8:r * 8 + 8, c * 8:c * 8 + 8].reshape(64, 3)).sum() == 0:
                continue
            best, idx = None, None
            for pb in range(16):
                cols = p[pb * 16 + 1:pb * 16 + 16]
                d = ((t[:, None, :] - cols[None]) ** 2).sum(2)
                score = d.min(1).sum()
                if best is None or score < best:
                    best, idx, bpb = score, d.argmin(1) + 1, pb
            e = m[r * 32 + c]
            assert not e & 0x0C00
            o = 0x30 + (e & 0x3FF) * 32
            for i in range(64):
                y, x = i // 8, i % 8
                a = o + y * 4 + x // 2
                b[a] = (b[a] & 0x0F) | int(idx[i]) << 4 if x & 1 else (b[a] & 0xF0) | int(idx[i])
            m[r * 32 + c] = (e & 0x0FFF) | bpb << 12
    struct.pack_into("<1024H", s, 0x24, *m)
    return bytes(b), bytes(s)
