"""Translation files: translation/en/<bank>.json maps string id to English.

In English text: \\n forces a line, \\f starts a page, {xxxx} is a raw token.
Lines wrap automatically; anything missing stays Japanese.
"""
import glob
import json
import os
import struct
import sys

import cardinfo
import drops
import entext

ADJUST = "translation/adjustments.json"
BANKS = range(2178, 2201)
MAX_W = 236
MAX_LINES = 3
CARD_BANK = 2193     # monster notes sit inside a framed panel
CARD_W = 208
LINES = {      # (bank, message): lines a page may keep, past the usual limit
    (2178, 33): 6, (2178, 34): 6,   # credits with the localization added: the credits show only a first page
}
BANK_LINES = {  # bank: lines any message's page may use, past its original's count
    2191: 6,    # item descriptions: the item box holds 6 (25 originals use 5, five use 6)
}
DIALOGUE = (*range(2178, 2191), 2194, 2195, 2196, 2198)   # 2198: the options' info boxes     # the talk box shows two lines unless the original used more


def load_bank(fid):
    b = open(f"work/lf2/{fid:05d}.bin", "rb").read()
    n = struct.unpack_from("<I", b, 0)[0] // 4
    off = struct.unpack_from(f"<{n}I", b, 0) + (len(b),)
    return b, [struct.unpack_from(f"<{(off[k + 1] - off[k]) // 2}H", b, off[k]) for k in range(n)]


def layout_limits():
    """Max lines per page and tokens per line in the original, per bank."""
    out = {}
    for fid in BANKS:
        _, rows = load_bank(fid)
        ml = mt = 0
        for s in rows:
            for page in " ".join(map(str, s[2:])).split(str(0xFFFE)):
                lines = page.split(str(0xFFFF))
                ml = max(ml, len(lines))
                mt = max(mt, max(len(l.split()) for l in lines))
        out[fid] = (ml, mt)
    return out


def split_page(lines, limit):
    """Cut an overlong page at the last sentence end in its first lines, or after them."""
    head = " ".join(lines[:limit])
    whole = " ".join(lines)
    cut = max(head.rfind(end) for end in (". ", "! ", "? ", "… "))
    cut = cut + 1 if cut >= 0 else len(head)
    return [whole[:cut], whole[cut + 1:]]


COLOURS = ("{fff7}", "{fff8}")     # a coloured name runs to {fffc}; the colour doesn't carry onto a new line


def words(para):
    """Words of a line, with each coloured span kept whole so it never breaks across lines."""
    out, span = [], None
    for word in para.split(" "):
        if span is not None:
            span.append(word)
        elif any(c in word for c in COLOURS) and "{fffc}" not in word.split(next(c for c in COLOURS if c in word), 1)[1]:
            span = [word]
            continue
        else:
            out.append(word)
            continue
        if "{fffc}" in word:
            out.append(" ".join(span))
            span = None
    if span is not None:        # coloured to the end: wrap() repeats the colour on each new line
        out += span
    return out


def open_colour(line):
    """The colour still on at the end of a line, if any."""
    best, at = None, line.rfind("{fffc}")
    for c in COLOURS:
        if line.rfind(c) > at:
            best, at = c, line.rfind(c)
    return best


def wrap(text, widths, max_lines=MAX_LINES, max_w=MAX_W, split=False):
    """Wrap to MAX_W, keeping forced lines and pages. Returns (text, problems).

    With split, a page that runs too long carries on to a new page."""
    problems = []
    pages = []
    waiting = text.split(chr(12))
    while waiting:
        page = waiting.pop(0)
        lines = []
        for para in page.split(chr(10)):
            cur, w = [], 0
            for word in words(para):
                ww = entext.text_width(entext.encode(word), widths)
                sp = 4 if cur else 0
                if cur and w + sp + ww > max_w:
                    lines.append(" ".join(cur))
                    c = open_colour(lines[-1])
                    cur, w = [c + word if c else word], ww
                else:
                    cur.append(word)
                    w += sp + ww
            lines.append(" ".join(cur))
        if split and len(lines) > max_lines:
            waiting[:0] = split_page(lines, max_lines)
            continue
        if len(lines) > max_lines:
            problems.append(f"{len(lines)}>{max_lines} lines: {lines[0][:34]}")
        for l in lines:
            if entext.text_width(entext.encode(l), widths) > max_w:
                problems.append(f"wide: {l[:34]}")
        pages.append(chr(10).join(lines))
    return chr(12).join(pages), problems


def orig_lines(s):
    """Most lines on any page of an original string."""
    best = cur = 1
    for t in s[2:]:
        if t == 0xFFFF:
            cur += 1
            best = max(best, cur)
        elif t == 0xFFFE:
            cur = 1
    return best


def line_limit(fid, row):
    n = max(orig_lines(row), BANK_LINES.get(fid, 0))
    return max(2, n) if fid in DIALOGUE else max(MAX_LINES, n)


def load_adjustments():
    """Hand adjustments saved from index.html: {"bank/id": English}, kept apart from the translation."""
    if not os.path.exists(ADJUST):
        return {}
    return json.load(open(ADJUST, encoding="utf-8"))


def base_strings(fid):
    strs = {}
    for p in sorted(glob.glob(f"translation/en/{fid}*.json")):
        strs.update(json.load(open(p, encoding="utf-8")))
    return strs


EXTRA = {}      # (bank, message): text made at build time, as the patch's version line


def load_strings(fid):
    """A bank's English with the hand adjustments applied, and the build's own lines (EXTRA)."""
    strs = base_strings(fid)
    for k, v in load_adjustments().items():
        bank, sid = k.split("/")
        if int(bank) == fid:
            strs[sid] = v
    for (bank, sid), v in EXTRA.items():
        if bank == fid:
            strs[str(sid)] = v
    return strs


def load_edits(widths):
    edits, report = {}, []
    done = total = 0
    for fid in BANKS:
        _, rows = load_bank(fid)
        total += len(rows)
        strs = load_strings(fid)
        if not strs:
            continue
        toks = {}
        if fid == CARD_BANK:
            enemies = drops.enemies()
            strs.update({str(k): v for k, v in cardinfo.texts(enemies).items()})
        for k, v in strs.items():
            if fid == CARD_BANK and int(k) >= drops.FIRST_ID and cardinfo.wrapped(int(k)):    # Detailed Info: wrapped like the notes
                head, body = v.split(chr(10) * 2, 1)
                w, probs = wrap(body, widths, 6, CARD_W)
                w = head + chr(10) * 2 + w
            elif fid == CARD_BANK and int(k) >= drops.FIRST_ID:     # Item Info: laid out already
                w, probs = v, [f"wide: {l[:34]}" for l in v.split(chr(10)) if entext.text_width(entext.encode(l), widths) > CARD_W]
            elif fid == CARD_BANK:
                head, body = v.split(chr(10) * 2, 1)
                w, probs = wrap(body.replace(chr(10), " "), widths, 6, CARD_W)
                w = head + chr(10) * 2 + w
            else:
                row = rows[int(k)] if int(k) < len(rows) else rows[-1]      # new messages past the bank's end
                w, probs = wrap(v, widths, LINES.get((fid, int(k)), line_limit(fid, row)), split=fid in DIALOGUE)
            report += [f"{fid}/{k}: {x}" for x in probs]
            toks[int(k)] = entext.encode(w)
        edits[fid] = toks
        done += len(toks)
    print(f"translated {done}/{total} strings")
    return edits, report


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1] == "limits":
        print(layout_limits())
