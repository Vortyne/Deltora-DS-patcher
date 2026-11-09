"""English font, text encoder, and ARM9 variable-width text patch."""
import struct

import numpy as np
import pixelfont
from keystone import Ks, KS_ARCH_ARM, KS_MODE_ARM
from PIL import Image, ImageDraw, ImageFont

ARM9_RAM = 0x02000000
DATA = 0x30                  # RGCN tile data offset
WIDTH_TABLE = 0x28400        # past the end of the RGCN; the whole file is loaded raw
DEFAULT_ADVANCE = 12
ARROW = "▼"     # menu pointer
PUNCTUATION = "\",.:;()/"
EDGE, SOLID = 0.3, 0.62      # glyph coverage: below EDGE empty, below SOLID soft shade

CHARMAP = {" ": 0xCF, ",": 0x03, ".": 0x04, "!": 0x09, "?": 0x0A, "\"": 0x0B,
           "'": 0xCE, "<": 0xCA, ">": 0xCB, ";": 0xCC, ":": 0xCD, "+": 0xEA,
           "-": 0xEB, "*": 0xEC, "/": 0xED, "=": 0xEE, "%": 0xEF, "&": 0xFA,
           "@": 0xFB, "(": 0xFC, ")": 0xFD, "…": 0x07, "~": 0x08}
CHARMAP.update({chr(65 + i): 0xB0 + i for i in range(26)})
CHARMAP.update({chr(97 + i): 0xD0 + i for i in range(26)})
CHARMAP.update({chr(48 + i): 0xF0 + i for i in range(10)})


A_BUTTON = "Ⓐ"
A_TOKEN = 0x3FE
X_BUTTON = "Ⓧ"
X_TOKEN = 0x3FD
EXTRA = {"♥": 0x100, A_BUTTON: A_TOKEN, X_BUTTON: X_TOKEN}   # 0x100 is a kept original glyph


def a_button():
    """The DS A button. Title text is dark on a light outline, so index 1 is the black."""
    px = np.zeros((16, 16), dtype=np.uint8)
    for y in range(14):
        for x in range(14):
            if (x - 6.5) ** 2 + (y - 6.5) ** 2 <= 46:
                px[y, x] = 1
    letter = ["   ##   ", "  ####  ", " ##  ## ", " ##  ## ", " ###### ", " ##  ## ", " ##  ## "]
    for y, row in enumerate(letter):
        for x, c in enumerate(row):
            if c == "#":
                px[y + 3, x + 3] = 15
    return px


def x_button():
    """The DS X button as a dialogue glyph: a filled circle with the letter cut out."""
    px = np.zeros((16, 16), dtype=np.uint8)
    disc = np.zeros((16, 16), dtype=bool)
    for y in range(14):
        for x in range(14):
            disc[y + 1, x] = (x - 6.5) ** 2 + (y - 6.5) ** 2 <= 46
    edge = np.zeros_like(disc)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        edge |= np.roll(np.roll(disc, dy, 0), dx, 1)
    px[edge & ~disc] = 15
    px[disc] = 1
    letter = [" ##  ## ", " ##  ## ", "  ####  ", "   ##   ", "  ####  ", " ##  ## ", " ##  ## "]
    for y, row in enumerate(letter):
        for x, c in enumerate(row):
            if c == "#":
                px[y + 4, x + 3] = 0
    return px


def hand_drawn(ch):
    """A pixelfont glyph, or two side by side, with a one pixel outline."""
    a = pixelfont.word(ch)
    w = a.shape[1]
    if w > 14:
        a = pixelfont.word(ch, 0)
        w = a.shape[1]
    fill = np.zeros((16, 16), dtype=bool)
    fill[3:3 + a.shape[0], 1:1 + w] = a
    edge = np.zeros_like(fill)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
        edge |= np.roll(np.roll(fill, dy, 0), dx, 1)
    px = np.zeros((16, 16), dtype=np.uint8)
    px[edge & ~fill] = 15
    px[fill] = 1            # one shade: palettes differ, so a ramp fades or darkens by screen
    return px, w + 2


def render_glyph(ch, font):
    """Return (16x16 array of pixel indices, advance)."""
    if ch == A_BUTTON:
        return a_button(), 15
    if ch == X_BUTTON:
        return x_button(), 15
    if ch.strip() and all(pixelfont.has(c) for c in ch.strip()):
        return hand_drawn(ch)
    # draw at 4x and reduce, so edge pixels keep their partial coverage
    big = ImageFont.load_default(size=font.size * 4)
    im = Image.new("L", (128, 128))
    ImageDraw.Draw(im).text((16, 56), ch, fill=255, font=big, anchor="ls")
    cov = np.asarray(im.resize((32, 32), Image.BOX)) / 255
    if ch == "!":
        # the font's stem is thin with no gap, which reads as a lowercase l
        cov = np.zeros((32, 32))
        cov[5:11, 4:6] = cov[12:14, 4:6] = 1
    elif ch == ARROW:
        cov = np.zeros((32, 32))
        for i in range(6):
            cov[6 + i, 4 + i:15 - i] = 1
    elif ch == "'":
        cov = np.zeros((32, 32))
        cov[5:9, 4:6] = 1
    elif ch in PUNCTUATION:
        cov = (cov >= EDGE).astype(float)   # too thin to survive the soft shade
    a = cov >= EDGE
    if not a.any():
        return np.zeros((16, 16), dtype=np.uint8), 4
    xs = np.where(a.any(0))[0]
    if len(ch) == 2 and xs[-1] - xs[0] + 1 > 14:
        # squeeze wide double-letter glyphs into the 14 usable pixels
        x0, x1 = xs[0], xs[-1] + 1
        sq = Image.fromarray((cov[:, x0:x1] * 255).astype(np.uint8)).resize((14, 32), Image.LANCZOS)
        cov = np.zeros((32, 32))
        cov[:, 4:18] = np.asarray(sq) / 255
        a = cov >= EDGE
        xs = np.where(a.any(0))[0]
    # keep the baseline: row 14 in the source maps to row 11 in the glyph
    fill = np.zeros((16, 16), dtype=bool)
    soft = np.zeros((16, 16), dtype=bool)
    w = min(xs[-1] - xs[0] + 1, 14)
    for y in range(32):
        ny = y - 14 + 11
        if 0 <= ny < 16:
            fill[ny, 1:1 + w] = a[y, xs[0]:xs[0] + w]
            soft[ny, 1:1 + w] = (cov[y, xs[0]:xs[0] + w] < SOLID) & a[y, xs[0]:xs[0] + w]
    outline = np.zeros_like(fill)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
        outline |= np.roll(np.roll(fill, dy, 0), dx, 1)
    outline &= ~fill
    px = np.zeros((16, 16), dtype=np.uint8)
    px[outline] = 15
    for y in range(16):
        px[y][fill[y]] = min(4, 1 + max(0, y - 2) // 3)
    px[soft] = 14       # the shade the Japanese glyphs use between fill and outline
    # spacing follows the solid strokes, so soft edges don't widen the text
    solid = np.where((cov >= 0.7).any(0))[0]
    return px, min(w, int(solid[-1] - xs[0]) + 1 if len(solid) else w) + 2


def name_font():
    return ImageFont.load_default(size=13)


def patch_font(rgcn, pairs=None):
    """Return an RGCN with Latin glyphs and the width table written into it.

    pairs maps two-letter strings to font slots for double-letter glyphs.
    """
    b = bytearray(rgcn)
    b.extend(bytes(DATA + WIDTH_TABLE + 0x400 - len(b)))
    font = ImageFont.load_default(size=13)
    widths = bytearray(0x400)
    for ch, t in list(CHARMAP.items()) + list((pairs or {}).items()):
        px, adv = render_glyph(ch, font)
        if len(ch) == 2:
            adv = min(adv + (3 if ch[1] == " " else 0), 16)
        widths[t] = adv
        base = DATA + ((t & 15) << 6) + ((t >> 4) << 11)
        for qy in range(2):
            for qx in range(2):
                for y in range(8):
                    for x in range(8):
                        v = int(px[qy * 8 + y, qx * 8 + x])
                        o = base + qy * 0x400 + qx * 0x20 + y * 4 + x // 2
                        if x & 1:
                            b[o] = (b[o] & 0x0F) | v << 4
                        else:
                            b[o] = (b[o] & 0xF0) | v
    b[DATA + WIDTH_TABLE:DATA + WIDTH_TABLE + 0x400] = widths
    return bytes(b), widths


def encode(text):
    """English string to tokens. \\n newline, \\f new page, {xxxx} raw token."""
    out = []
    i = 0
    while i < len(text):
        c = text[i]
        if c == "{":
            e = text.index("}", i)
            out.append(int(text[i + 1:e], 16))
            i = e + 1
            continue
        if c == "\n":
            out.append(0xFFFF)
        elif c == "\f":
            out.append(0xFFFE)
        else:
            out.append(EXTRA[c] if c in EXTRA else CHARMAP[c])
        i += 1
    return out


def text_width(tokens, widths):
    """Widest line in pixels, for overflow checks."""
    best = cur = 0
    for t in tokens:
        if t in (0xFFFF, 0xFFFE, 0xFFFD):
            best, cur = max(best, cur), 0
        elif t == 0xFFF4:
            cur += 6
        elif t < 0x400:
            cur += widths[t] or DEFAULT_ADVANCE
    return max(best, cur)


def rebuild_bank(orig, edits):
    """edits: {string_id: token list}; the two header words are kept."""
    n = struct.unpack_from("<I", orig, 0)[0] // 4
    off = struct.unpack_from(f"<{n}I", orig, 0) + (len(orig),)
    parts, offs = [], []
    pos = n * 4
    for k in range(n):
        raw = orig[off[k]:off[k + 1]]
        if k in edits:
            raw = raw[:4] + struct.pack(f"<{len(edits[k])}H", *edits[k]) + b"\xFD\xFF"
        offs.append(pos)
        parts.append(raw)
        pos += len(raw)
    extra = sorted(k for k in edits if k >= n)          # new messages: appended, with an empty header
    assert extra == list(range(n, n + len(extra))), extra
    if extra:
        offs = [o + 4 * len(extra) for o in offs]
        pos += 4 * len(extra)
        for k in extra:
            raw = bytes(4) + struct.pack(f"<{len(edits[k])}H", *edits[k]) + b"\xFD\xFF"
            offs.append(pos)
            parts.append(raw)
            pos += len(raw)
    return struct.pack(f"<{len(offs)}I", *offs) + b"".join(parts)


def asm(src, addr):
    """Keystone prints some errors (an out-of-range adr) to stderr and still returns code, with
    a wrong instruction in place: catch its stderr and fail the build instead."""
    import os, tempfile
    with tempfile.TemporaryFile() as err:
        saved = os.dup(2)
        os.dup2(err.fileno(), 2)
        try:
            enc, _ = Ks(KS_ARCH_ARM, KS_MODE_ARM).asm(src, addr)
        finally:
            os.dup2(saved, 2)
            os.close(saved)
        err.seek(0)
        text = err.read().decode(errors="replace")
    if "error" in text.lower():
        raise ValueError(f"assembler at {addr:#x}: {text.strip()}")
    return bytes(enc)


MEASURE = 0x0204D9C4
MEASURE_END = 0x0204DACC
ADV_SITE = 0x0204DFCC


def patch_arm9(arm9):
    b = bytearray(arm9)

    def put(addr, code):
        b[addr - ARM9_RAM:addr - ARM9_RAM + len(code)] = code

    # Replaces the fixed-width line measure. glyph_width sits after it.
    src = """
        push {r4, r5, r6, r7, lr}
        mov r7, r0
        mov r4, r1
        mov r5, r2
        mov r6, #0
    loop:
        cmp r5, #0
        beq done
        sub r5, r5, #1
        ldrsh r0, [r4], #2
        cmp r0, #0
        bge glyph
        cmn r0, #3
        bge done
        cmn r0, #12
        addeq r6, r6, #6
        ldrlt r1, [r7, #0x40]   @ below -12 (as %7d's padding, 0x81F4): the renderer moves one
        addlt r6, r6, r1        @ letter spacing for these, so the line is that much wider
        b loop
    glyph:
        bl glyph_width
        add r6, r6, r0
        b loop
    done:
        ldr r1, [r7, #0x38]
        cmp r1, #0
        rsbeq r0, r6, #0xff
        popeq {r4, r5, r6, r7, pc}
        cmp r1, #1
        movne r0, #0
        rsbeq r0, r6, #0x100
        addeq r0, r0, r0, lsr #31
        asreq r0, r0, #1
        pop {r4, r5, r6, r7, pc}
    glyph_width:
        ldr r3, =0x021DDF34
        ldrb r2, [r3]
        cmp r2, #0
        ldreq r3, [r3, #0x14]
        ldrne r3, [r3, #0x20]
        add r3, r3, #0x28400
        cmp r0, #0x400
        movhs r0, #12
        bxhs lr
        ldrb r0, [r3, r0]
        cmp r0, #0
        moveq r0, #12
        bx lr
    advance:
        ldr r1, [sp, #0x1C]
        ldr r0, [sp, #0x10]
        add r0, r1, r0, lsl #1
        ldrsh r0, [r0]
        push {lr}
        bl glyph_width
        pop {lr}
        ldr r1, [sp, #0x18]
        add r0, r0, r1
        bx lr
    """
    code = asm(src, MEASURE)
    assert MEASURE + len(code) <= MEASURE_END, len(code)
    put(MEASURE, code)
    adv = MEASURE + code_label_offset(code)
    # ldr r1,[sb,#0x40] / ldr r0,[sp,#0x18] / add r0,r0,r1 / str r0,[sp,#0x18]
    site = asm(f"bl {adv:#x}; nop; nop", ADV_SITE)
    put(ADV_SITE, site)
    return bytes(b)


def code_label_offset(code):
    """Offset of `advance:`, found by its first instruction."""
    return code.index(asm("ldr r1, [sp, #0x1C]", 0))
