"""Enemy drops for the card book's Item Info view.

File 2377 holds one 596-byte record per enemy. Its drop table is 8 entries of
(tag, item, weight, 0) at +0x12C; an entry is used when tag is nonzero. One roll
in 0..0xFFFF picks the entry whose running weight passes it, so weight / 65536 is
the chance per kill. Items: 0-111 bag items (names in 2197 from 72), 112-115
money (1, 10, 100, 500), 116-227 cards. A card's later, stronger enemy has its
own record; the view lists what either record drops.
"""
import struct

import translate

ENEMIES = "work/lf2/02377.bin"
STRIDE, TABLE = 596, 0x12C
CARD0, CARDS = 116, 112
MONEY = range(112, 116)
FIRST_ID = 112          # Item Info for card k is message 112 + k of bank 2193


# Crafting materials and gear drop at least this often (weight / 65536 per kill: 6.25%). Raising
# a weight only takes from the share of the roll that drops nothing; every table has room.
MIN_WEIGHT = 4096
RAISED = ("Iron", "Crystal", "Gold", "Silver", "Guard's Armour", "Gold Armband", "Poncho",
          "Pirate's Armour", "Pointy Hat", "Frog Flippers")
OWN_MIN = {"Poncho": 8192}      # 12.5%: only Mimics drop it, and in the story each is met alone


def enemies():
    """File 2377 as the game gets it: the drop weights in RAISED brought up to MIN_WEIGHT."""
    data = bytearray(open(ENEMIES, "rb").read())
    lab = translate.load_strings(2197)
    items = {lab[str(72 + i)]: i for i in range(112)}
    raise_ = {items[name]: OWN_MIN.get(name, MIN_WEIGHT) for name in RAISED}
    for r in range(len(data) // STRIDE):
        at = r * STRIDE + TABLE
        rows = [struct.unpack_from("<hHHH", data, at + 8 * i) for i in range(8)]
        for i, (tag, item, weight, _) in enumerate(rows):
            if tag and item in raise_ and weight < raise_[item]:
                struct.pack_into("<H", data, at + 8 * i + 4, raise_[item])
        total = sum(struct.unpack_from("<H", data, at + 8 * i + 4)[0] for i in range(8)
                    if struct.unpack_from("<h", data, at + 8 * i)[0])
        assert total <= 0x10000, (r, total)
    return bytes(data)


def tables(data):
    """{card: [drop tables]} for every enemy whose table holds its card."""
    out = {}
    for r in range(len(data) // STRIDE):
        drops = [struct.unpack_from("<hHHH", data, r * STRIDE + TABLE + 8 * i) for i in range(8)]
        drops = [(item, weight) for tag, item, weight, _ in drops if tag]
        for item, _ in drops:
            if CARD0 <= item < CARD0 + CARDS:
                out.setdefault(item - CARD0, []).append(drops)
    return out


def percent(weight):
    hundredths = (weight * 10000 + 32768) // 65536       # rounded half up: 3.125 shows as 3.13
    return f"{hundredths // 100}.{hundredths % 100:02d}".rstrip("0").rstrip(".") + "%"


def lines(found):
    """Item lines in first-seen order, then money. The card's own chance isn't listed."""
    items, money = {}, 0
    for drops in found:
        money = max(money, sum(w for item, w in drops if item in MONEY))
        for item, w in drops:
            if item < 112:
                items[item] = max(items.get(item, 0), w)
    lab = translate.load_strings(2197)
    out = [(lab[str(72 + item)], w) for item, w in items.items()]
    if money:
        out.append(("Money", money))
    return [f"{name}  {percent(w)}" for name, w in out]


def texts(data):
    """{message id: text} for bank 2193: each card's name, then its drops."""
    notes = translate.load_strings(2193)
    found = tables(data)
    out = {}
    for k in range(CARDS):
        name = notes[str(k)].split("\n")[0]
        rows = (lines(found[k]) if k in found else []) or ["No item drops."]
        assert len(rows) <= 5, rows
        out[FIRST_ID + k] = name + "\n\n" + "\n".join(rows)
    return out


def slots(data):
    """Kill counter slot per card (255: none), and how many slots."""
    found = sorted(tables(data))
    return bytes(found.index(k) if k in found else 255 for k in range(CARDS)), len(found)
