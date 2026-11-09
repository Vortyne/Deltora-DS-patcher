"""The card book's Detailed Info view: each fought enemy's HP and where it turns up.

Enemy records (drops.ENEMIES, 596 bytes each) keep HP at +0xCC; +0xC8 is 1 for bosses.
A spawn record names an enemy as 0x8000 | (record + 1); kind 2 is a placed enemy and
kinds 10-28 are bosses. Where: the stage table in the ARM9 (STAGES: chapter * 0xA10 +
stage * 0x142, then 20 areas of 8 halfwords; +12 is the area script) ties each area
script to its spawn files, and the stage's CampSet(camp, x, y) names the place: save
screen name 15 + camp in bank 2192. The Tower of Illusion (script 2612) spawns records
108 + 6 * (floor / 10) + a random step, so records from 108 on are the Tower's.

Cards with no enemy record are people met along the way: they get no Item Info and no
Detailed Info.
"""
import paths
import glob
import struct

import drops
import scr
import translate

ROM = paths.ROM
ARM9, ARM9_SIZE, RAM = 0x4000, 845752, 0x02000000
STAGES = 0x020BAA70
CHAPTERS, STAGE_ROOM, AREAS = range(10), 8, 20
HP, BOSS = 0xCC, 0xC8
FIRST_ID = 224          # Detailed Info for card k is message 224 + k of bank 2193
TOWER_SHIFT = 224       # once the Tower is open: Item Info at 336 + k, Detailed Info at 448 + k
TOWER_MARK = " (Tower)"  # an Item Info drop only Tower copies give
SPAWN_FILES = range(2600, 2960)
TOWER_FROM = 108
FARM_STAGE, TOWER_CHAPTER = (0, 2), 9
SAME_PLACE = {(1, 5): (1, 6)}  # Mokeet's Mansion's first rooms: no camp of their own, the mansion's music
FARM, TOWER = "Grand Farm", "Tower of Illusion"     # as bank 2197 names them
# Boss cards and their records: the boss kinds their own stage spawns (kind in comments).
BOSSES = {
    46: [3],            # Wennbar, kind 10
    47: [4, 98],        # Gorl, kind 11; 98 is its Tower copy (same model and attacks)
    48: [16],           # Soldeen, kind 12
    49: [27],           # Reeah, kind 13
    50: [38],           # The Sand Beast, kind 15
    51: [52],           # Vraal, kind 16
    52: [53],           # Gellick, kind 17
    53: [62],           # The Glus: script 2511 spawns record 62
    54: [63],           # Thaegan, kind 19
    55: [72],           # the Guardian, kind 20
    56: [64, 104],      # Ichabod, kind 22; 104 is its Tower copy
    57: [87, 88],       # Fallow, kinds 23 and 25
    61: [26, 130],      # the Ra-Kacharz in Noradz (800 HP, no drops); 130 is their Tower copy (same model)
    66: [37],           # Doom at the Rithmere games, kind 14
    72: [85, 86],       # Dain, kinds 21 and 24
    102: [92],          # the Grand Serpent at the Grand Farm, kind 26
    **{95 + i: [99 + i] for i in range(5)},     # the Tower's five dragons (floors 20, 40, 60, 80, 99):
}                                               # records 99-103, one model in five variants, HP 3000-7000
DRAGONS = range(99, 104)    # the Tower spawns them through its own boss object, not a spawn file


def record(data, r, at):
    return struct.unpack_from("<i", data, r * drops.STRIDE + at)[0]


def card_records(data):
    """{card: [records]}: the records whose drops hold the card, and the bosses."""
    out = {}
    for r in range(len(data) // drops.STRIDE):
        for i in range(8):
            tag, item = struct.unpack_from("<hH", data, r * drops.STRIDE + drops.TABLE + 8 * i)
            if tag and drops.CARD0 <= item < drops.CARD0 + drops.CARDS:
                out.setdefault(item - drops.CARD0, []).append(r)
    for card, rs in BOSSES.items():
        assert card not in out, card
        assert all(record(data, r, BOSS) == 1 for r in rs), card
        out[card] = rs
    return out


def script_ops(fid):
    b = open(f"work/lf2/{fid:05d}.bin", "rb").read()
    if b[:4] != b"SCR0":
        return
    funcs, imports = scr.recs(b)
    names = [scr.rec(b, o)["name"] if o else "" for o in imports]
    for o in funcs:
        if o:
            ints = []
            for _, op in scr.walk(b, scr.rec(b, o)):
                if op[0] == "push" and isinstance(op[2], int):
                    ints.append(op[2])
                    yield "push", op[2]
                elif op[0] == "call":
                    if op[1] == 0x2102:
                        yield names[op[2]], ints
                    ints = []


def stage_areas():
    """{(chapter, stage): [area scripts]} from the ARM9's stage table."""
    a = open(ROM, "rb").read()[ARM9:ARM9 + ARM9_SIZE]
    out = {}
    for c in CHAPTERS:
        for s in range(STAGE_ROOM):
            at = STAGES - RAM + c * 0xA10 + s * 0x142 + 2
            scripts = [struct.unpack_from("<H", a, at + 16 * k + 12)[0] for k in range(AREAS)]
            scripts = [x for x in scripts if x and 1700 < x < 2700]
            if scripts:
                out[(c, s)] = scripts
    return out


def place_names():
    """{(chapter, stage): place}, by the stage's camp; a stage without one takes its
    chapter's nearest camp, the one before it first."""
    names = translate.load_strings(2192)
    camps = {}
    for key, scripts in stage_areas().items():
        for sc in scripts:
            for name, ints in script_ops(sc):
                if name in ("CampSet", "CampSet2") and len(ints) >= 3 and key not in camps:
                    camps[key] = ints[-3]
    out = {}
    for c, s in stage_areas():
        if c == TOWER_CHAPTER:
            out[(c, s)] = TOWER
        elif (c, s) == FARM_STAGE:
            out[(c, s)] = FARM
        elif 1 <= c < TOWER_CHAPTER:
            same = sorted(k for k in camps if k[0] == c)
            near = [SAME_PLACE[(c, s)]] if (c, s) in SAME_PLACE else                 [k for k in same if k[1] <= s][-1:] or [k for k in same if k[1] > s][:1]
            text = names[str(15 + camps[near[0]])].replace("{fff8}", "").replace("\n", " ")
            text = text.replace("Special Stage ", "")         # Mokeet's Mansion (CampSet2) stands alone
            out[(c, s)] = " ".join(w for w in text.split() if w != "Entrance")    # "City of the Rats", not its entrance
    return out


def spawn_records(fid):
    d = open(f"work/lf2/{fid:05d}.bin", "rb").read()
    out = set()
    for screen in range(64):
        k = struct.unpack_from("<h", d, screen * 2)[0]
        if k < 0:
            continue
        p = 0x80 + k * 0x1C
        while p + 0x1C <= len(d) and struct.unpack_from("<H", d, p)[0] != 0xFFFF:
            kind, rid = struct.unpack_from("<HH", d, p)
            if (kind == 2 or 10 <= kind <= 28) and rid & 0x8000:
                out.add((rid & 0x7FFF) - 1)
            p += 0x1C
    return out


def where():
    """{record: [places]} in the order the game reaches them."""
    names = place_names()
    found = {}
    for key, scripts in sorted(stage_areas().items()):
        if key not in names:
            continue
        for sc in scripts:
            for name, ints in script_ops(sc):
                if name == "push" and ints in SPAWN_FILES:
                    rs = spawn_records(ints)
                elif name == "Spawn" and len(ints) == 7 and ints[0] in (0, 2) and ints[1] == 0:
                    rs = {ints[2] - 1}          # Spawn(kind, 0, record + 1, ...)
                else:
                    continue
                for r in rs:
                    found.setdefault(r, [])
                    if names[key] not in found[r]:
                        found[r].append(names[key])
    for r in [*DRAGONS, *range(TOWER_FROM, len(drops.enemies()) // drops.STRIDE)]:
        found.setdefault(r, [])
        if TOWER not in found[r]:
            found[r].append(TOWER)
    return found


def chapter_lines(places):
    """One line per chapter: "Ch. 6: Along the River Tor, Cave"; the farm and Tower stand alone."""
    groups = {}
    for p in places:
        words = p.split()
        if words[0] == "Chapter":
            head, rest = "Ch. " + words[1], " ".join(words[2:])
        elif words[:2] == ["Final", "Chapter"]:
            head, rest = "Final Ch.", " ".join(words[2:])
        else:
            head, rest = p, None
        groups.setdefault(head, [])
        if rest:
            groups[head].append(rest)
    return [head + (": " + ", ".join(rest) if rest else "") for head, rest in groups.items()]


def drop_table(data, r):
    """[(item, weight)] of record r's drop table."""
    rows = [struct.unpack_from("<hHHH", data, r * drops.STRIDE + drops.TABLE + 8 * i) for i in range(8)]
    return [(item, weight) for tag, item, weight, _ in rows if tag]


def item_rows(data, main, tower):
    """Item Info lines as drops.lines makes them; with tower records, what only they drop is marked."""
    plain = drops.lines([drop_table(data, r) for r in main])
    if not tower:
        return plain
    rows = drops.lines([drop_table(data, r) for r in main + tower])
    names = {row.rsplit("  ", 1)[0] for row in plain}
    return [row if row.rsplit("  ", 1)[0] in names else row + TOWER_MARK for row in rows]


def texts(data):
    """{message id: text} for bank 2193, from 112: Item Info, then Detailed Info, each first as
    it shows before the Tower of Illusion opens and then (from 336) after. translate wraps the
    Detailed Info lines under the name to the card's width; Item Info is laid out here."""
    notes = translate.load_strings(2193)
    recs = card_records(data)
    found = where()
    out = {}
    for k in range(drops.CARDS):
        name = notes[str(k)].split("\n")[0]
        rs = recs.get(k, [])
        tower = [r for r in rs if found.get(r) == [TOWER]]
        main = [r for r in rs if r not in tower] or rs
        tower = [r for r in rs if r not in main]
        tower_only = bool(rs) and all(found.get(r) == [TOWER] for r in rs)    # the dragons: met nowhere else
        hps = lambda group: " / ".join(str(x) for x in sorted(record(data, r, HP) for r in group))
        for shift, shown in ((0, main), (TOWER_SHIFT, rs)):
            items = item_rows(data, main, [r for r in shown if r not in main]) if rs else []
            assert len(items) <= 5, (k, items)
            out[drops.FIRST_ID + shift + k] = name + "\n\n" + "\n".join(items or ["No item drops."])
            hp = "HP: " + hps(main)
            if shown != main:
                hp += "  (Tower: " + hps(tower) + ")"
            places = []
            for r in shown:
                for p in found.get(r, []):
                    if p not in places and (p != TOWER or shown != main or tower_only):
                        places.append(p)
            rows = [hp] + chapter_lines(places) if rs else []      # people met: never shown
            out[FIRST_ID + shift + k] = name + "\n\n" + "\n".join(rows)
    return out


def wrapped(message):
    """True for Detailed Info, which translate wraps; Item Info is laid out already."""
    return (message - drops.FIRST_ID) % TOWER_SHIFT >= drops.CARDS


def slots(data):
    """drops.slots with each boss marked 254: no kill counter, but Item and Detailed Info.
    255 stays for people met, who have neither."""
    table, n = drops.slots(data)
    recs = card_records(data)
    out = bytes(254 if table[k] == 255 and k in recs else table[k] for k in range(drops.CARDS))
    assert all((x != 255) == (k in recs) for k, x in enumerate(out))
    return out, n


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    data = drops.enemies()
    for k, t in sorted(texts(data).items()):
        print(k, t.replace("\n", " | "))
