"""Item and card names stored in the database file 2176 (300-byte records).

The game copies these names into 11-token stack buffers and only writes an end
marker when it finds a zero, so a name must fit in 10 tokens or the game crashes.
English fits by packing two letters into one glyph, using font slots that the
translated text no longer needs.
"""
import json
import struct

import entext
import translate

STRIDE = 300
ITEM_BASE = 8           # record 0 name
CARD_BASE = 0x87FA      # first card name
ICON_CARD_BASE = 0x10B3A  # same names, after a card icon token
ITEMS = 112
CARDS = 112
MAX_TOKENS = 10

# Names too long for 10 tokens even when packed
SHORT = {
    "Child in the Purple Cloak": "Purple-Cloak Child",
    "Deltora Complete Collection": "Deltora Music Set",
    "The Belt of Deltora": "Belt of Deltora",
    "Bubble Pipe of Light": "Bubble Pipe",
    "The Cloak Mother Made": "Mother's Cloak",
    "Woman in the Pink Dress": "Woman in Pink",
    "Reeah the Great Snake": "Great Snake Reeah",
    "Guardian and Monsters": "Guardian & Beasts",
    "Captain and Polypan": "Captain & Polypan",
}


# Card names have one token less, for the code before them
SHORT_ICON = {
    "Purple Caterpillar": "Purple Grub",
    "Poison Bloodsucker": "Poison Leech",
    "Purple-Cloak Child": "Purple Child",
}


class Packer:
    """Assigns double-letter glyphs to font slots."""

    def __init__(self, free, font):
        self.free = list(free)
        self.font = font
        self.pairs = {}

    def fits(self, pair):
        if pair[0] == " " or pair not in self.pairs and not self.free and pair not in self.pairs:
            return False
        l, _, r, _ = self.font.getbbox(pair)
        return r - l <= 19

    def encode(self, text, limit):
        """Fewest tokens for text, using as few new pairs as possible."""
        n = len(text)
        best = [None] * (n + 1)
        best[n] = (0, [])
        for i in range(n - 1, -1, -1):
            c, rest = best[i + 1]
            best[i] = (c + 1, [text[i]] + rest)
            if i + 1 < n and self.fits(text[i:i + 2]) and best[i + 2][0] + 1 < best[i][0]:
                c, rest = best[i + 2]
                best[i] = (c + 1, [text[i:i + 2]] + rest)
        # greedy table gives the minimum; keep pairs only as far as needed
        parts = best[0][1]
        spare = limit - len(parts)
        if spare < 0:
            raise ValueError(f"{text!r} needs {len(parts)} tokens")
        out = []
        for p in parts:
            if len(p) == 2 and spare > 0 and p not in self.pairs:
                out += list(p)
                spare -= 1
            else:
                out.append(p)
        toks = []
        for p in out:
            if len(p) == 1:
                toks.append(entext.CHARMAP[p])
            else:
                if p not in self.pairs:
                    self.pairs[p] = self.free.pop(0)
                toks.append(self.pairs[p])
        return toks


def _put(b, off, toks):
    """Replace the zero-terminated token name at off."""
    i = off
    while struct.unpack_from("<H", b, i)[0] != 0:
        struct.pack_into("<H", b, i, 0)
        i += 2
    if i == off:
        return False
    for k, t in enumerate(toks):
        struct.pack_into("<H", b, off + k * 2, t)
    return True


def check(b):
    """Each name is copied as 11 tokens from record offset 8; one must be zero."""
    for r in range((len(b) - 8) // STRIDE):
        t = struct.unpack_from("<11H", b, r * STRIDE + 8)
        if 0 not in t:
            raise ValueError(f"record {r} has no end marker: {t}")


def patch(data, packer):
    b = bytearray(data)
    lab = translate.load_strings(2197)
    notes = translate.load_strings(2193)
    n = 0
    for r in range(ITEMS):
        off = ITEM_BASE + r * STRIDE
        if 48 <= r < 64:              # recipes: keep the leading icon token
            n += _put(b, off + 2, packer.encode(f"Recipe {r - 47}", MAX_TOKENS - 1))
            continue
        name = lab.get(str(72 + r))
        if name:
            n += _put(b, off, packer.encode(SHORT.get(name, name), MAX_TOKENS))
    for k in range(CARDS):
        name = notes[str(k)].split("\n")[0]
        name = SHORT.get(name, name)
        # a colour code sits before the name, so the limit is one lower
        n += _put(b, CARD_BASE + k * STRIDE, packer.encode(SHORT_ICON.get(name, name), MAX_TOKENS - 1))
        n += _put(b, ICON_CARD_BASE + k * STRIDE, packer.encode(SHORT_ICON.get(name, name), MAX_TOKENS - 1))
    check(b)
    return bytes(b), n
