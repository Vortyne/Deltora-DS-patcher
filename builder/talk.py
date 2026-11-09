"""How close each placed character must be before its touch script talks.

A character placed by an area's spawn file (AreaSpawn) keeps its record's id at
object +0x410. Its record names a script; that script's Mob_Touch usually starts
with GetMobDistance(player, it) / 4096 < N and does nothing past N pixels. A
uses the same check, so it never picks someone who won't answer.
"""
import glob
import struct

import scr
from lf2 import lf

DEFAULT = 48            # chests (scripts 2235-2238), and anyone without a record
RECORD = 0x1C


def limit(script):
    """The Mob_Touch distance limit in pixels, or None."""
    try:
        b = lf(script)
    except OSError:
        return None
    if b[:4] != b"SCR0":
        return None
    funcs, imports = scr.recs(b)
    names = [scr.rec(b, o)["name"] if o else "" for o in imports]
    for o in funcs:
        if not o or scr.rec(b, o)["name"] != "Mob_Touch":
            continue
        ops = list(scr.walk(b, scr.rec(b, o)))
        for k, (_, op) in enumerate(ops):
            if op[0] == "call" and op[1] == 0x2102 and names[op[2]] == "GetMobDistance":
                div, n, less = (x[1] for x in ops[k + 1:k + 5][1:])
                if div == ("op", 6, None) and n[0] == "push" and less == ("op", 9, None):
                    return n[2]
    return None


def spawn_files():
    """Every file a script's AreaSpawn names."""
    out = set()
    for f in glob.glob("work/lf2/*.bin"):
        b = open(f, "rb").read()
        if b[:4] != b"SCR0":
            continue
        funcs, imports = scr.recs(b)
        names = [scr.rec(b, o)["name"] if o else "" for o in imports]
        for o in funcs:
            if not o:
                continue
            last = None
            for _, op in scr.walk(b, scr.rec(b, o)):
                if op[0] == "push":
                    last = op[2] if last is None else last
                elif op[0] == "call":
                    if op[1] == 0x2102 and names[op[2]] == "AreaSpawn" and isinstance(last, int):
                        out.add(last)
                    last = None
                elif op[0] == "op" and op[1] in (0xA000, 0x108, 0x101, 0x103, 0x14):
                    last = None
    return sorted(out)


def limits():
    """{spawn id: limit} for characters whose limit isn't DEFAULT."""
    found = {}
    for f in spawn_files():
        d = lf(f)
        for screen in range(64):
            k = struct.unpack_from("<h", d, screen * 2)[0]
            if k < 0:
                continue
            p = 0x80 + k * RECORD
            while p + RECORD <= len(d) and struct.unpack_from("<H", d, p)[0] != 0xFFFF:
                kind, sid, script = (struct.unpack_from("<H", d, p + o)[0] for o in (0, 20, 24))
                if kind in (1, 3):
                    found.setdefault(sid, set()).add(limit(script))
                p += RECORD
    out = {}
    for sid, ns in found.items():
        assert len(ns) == 1, (sid, ns)         # one id, one character
        n = ns.pop()
        if n is not None and n != DEFAULT:
            out[sid] = n
    return out


def table():
    """u16 entries: id | limit / 4 << 12, then 0."""
    out = []
    for sid, n in sorted(limits().items()):
        assert 0 < sid < 0x1000 and n % 4 == 0 and n < 64, (sid, n)
        out.append(sid | n // 4 << 12)
    return struct.pack(f"<{len(out) + 1}H", *out, 0)
