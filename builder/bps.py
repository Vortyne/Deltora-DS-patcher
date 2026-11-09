"""BPS patches (the beat format Floating IPS and the web patcher read), to ship the English ROM
as a difference from the original.

create() covers three cases, which is all this ROM needs: data at the same place in both (most
of it), data that moved (the video file, archive entries), and new bytes, stored as they are.
"""
import zlib

SOURCE_READ, TARGET_READ, SOURCE_COPY = 0, 1, 2
BLOCK = 256         # moved data is found by whole aligned blocks of the original
MIN_SAME = 32       # shorter same-place runs go out as literal bytes


def _varint(n):
    out = bytearray()
    while True:
        x = n & 0x7F
        n >>= 7
        if n == 0:
            out.append(0x80 | x)
            return out
        out.append(x)
        n -= 1


def _same(a, i, b, j, limit):
    """How many bytes a[i:] and b[j:] share, up to limit."""
    n = 0
    while n < limit:
        k = min(4096, limit - n)
        if a[i + n:i + n + k] == b[j + n:j + n + k]:
            n += k
            continue
        while a[i + n] == b[j + n]:         # the chunk differs somewhere: find where
            n += 1
        break
    return n


def create(source, target):
    index = {}
    for p in range(0, len(source) - BLOCK + 1, BLOCK):
        block = source[p:p + BLOCK]
        if block.count(block[:1]) != BLOCK:                 # one-byte fills don't tell places apart
            index.setdefault(hash(block), p)
    out = bytearray(b"BPS1")
    out += _varint(len(source)) + _varint(len(target)) + _varint(0)
    t = 0
    lit = None              # where pending literal bytes start
    src_rel = 0             # SourceCopy offsets are relative to the last one's end
    n = len(target)

    def flush(upto):
        nonlocal lit
        if lit is not None and upto > lit:
            out.extend(_varint((upto - lit - 1) << 2 | TARGET_READ))
            out.extend(target[lit:upto])
        lit = None

    while t < n:
        # the same place in both
        if t < len(source) and target[t:t + MIN_SAME] == source[t:t + MIN_SAME]:
            k = _same(target, t, source, t, min(n, len(source)) - t)
            if k >= MIN_SAME:
                flush(t)
                out += _varint((k - 1) << 2 | SOURCE_READ)
                t += k
                continue
        # moved from elsewhere in the original
        s = index.get(hash(target[t:t + BLOCK])) if t + BLOCK <= n else None
        if s is not None and target[t:t + BLOCK] == source[s:s + BLOCK]:
            back = 0                                         # take back literal bytes that match too
            while lit is not None and t - back > lit and s - back > 0 and target[t - back - 1] == source[s - back - 1]:
                back += 1
            t, s = t - back, s - back
            flush(t)
            k = _same(target, t, source, s, min(n - t, len(source) - s))
            d = s - src_rel
            out += _varint((k - 1) << 2 | SOURCE_COPY) + _varint(abs(d) << 1 | (d < 0))
            src_rel = s + k
            t += k
            continue
        if lit is None:
            lit = t
        t += 1
    flush(n)
    out += zlib.crc32(source).to_bytes(4, "little") + zlib.crc32(target).to_bytes(4, "little")
    out += zlib.crc32(out).to_bytes(4, "little")
    return bytes(out)


def apply(source, patch):
    """The reference decoder, to check a patch before it's published."""
    def varint():
        nonlocal p
        n, shift = 0, 1
        while True:
            x = patch[p]
            p += 1
            n += (x & 0x7F) * shift
            if x & 0x80:
                return n
            shift <<= 7
            n += shift
    assert patch[:4] == b"BPS1"
    assert zlib.crc32(patch[:-4]) == int.from_bytes(patch[-4:], "little"), "patch damaged"
    p = 4
    src_size, tgt_size, meta = varint(), varint(), varint()
    p += meta
    assert len(source) == src_size and zlib.crc32(source) == int.from_bytes(patch[-12:-8], "little"), "wrong source"
    out = bytearray(tgt_size)
    o = s_rel = t_rel = 0
    end = len(patch) - 12
    while p < end:
        x = varint()
        cmd, k = x & 3, (x >> 2) + 1
        if cmd == SOURCE_READ:
            out[o:o + k] = source[o:o + k]
        elif cmd == TARGET_READ:
            out[o:o + k] = patch[p:p + k]
            p += k
        elif cmd == SOURCE_COPY:
            d = varint()
            s_rel += -(d >> 1) if d & 1 else d >> 1
            out[o:o + k] = source[s_rel:s_rel + k]
            s_rel += k
        else:
            d = varint()
            t_rel += -(d >> 1) if d & 1 else d >> 1
            for i in range(k):
                out[o + i] = out[t_rel + i]
            t_rel += k
        o += k
    assert zlib.crc32(out) == int.from_bytes(patch[-8:-4], "little"), "result doesn't match"
    return bytes(out)
