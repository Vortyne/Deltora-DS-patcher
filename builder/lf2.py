"""LF2 archive (FILEDATA.BIN) and Nintendo bottom-LZ (ARM9) helpers."""
import struct


def read_lf2(blob):
    """Return list of (byte_offset, size). Offsets are stored in 4-byte units."""
    magic, first, count, hdr = struct.unpack_from("<4I", blob, 0)
    assert blob[:4] == b"LF 2"
    out = []
    for i in range(count):
        o, s = struct.unpack_from("<II", blob, hdr + i * 8)
        out.append((o * 4, s))
    return out


def blz_decompress(data):
    """Decompress a BLZ blob that spans all of `data` (footer at the end)."""
    enc_len_flags, inc = struct.unpack_from("<II", data, len(data) - 8)
    hdr_len = enc_len_flags >> 24
    enc_len = enc_len_flags & 0xFFFFFF
    start = len(data) - enc_len
    out = bytearray(data[:len(data)] + bytes(inc))
    src = len(data) - hdr_len
    dst = len(out)
    while src > start and dst > start:
        src -= 1
        flags = data[src]
        for _ in range(8):
            if src <= start:
                break
            if flags & 0x80:
                src -= 2
                pair = data[src] | data[src + 1] << 8
                disp = (pair & 0xFFF) + 3
                ln = (pair >> 12) + 3
                for _ in range(ln):
                    dst -= 1
                    out[dst] = out[dst + disp]
            else:
                src -= 1
                dst -= 1
                out[dst] = data[src]
            flags = flags << 1 & 0xFF
    return bytes(out)


def lf(i):
    return open(f"work/lf2/{i:05d}.bin", "rb").read()


def lz10(b):
    size = int.from_bytes(b[1:4], "little")
    o = bytearray(); p = 4
    while len(o) < size:
        f = b[p]; p += 1
        for i in range(8):
            if len(o) >= size:
                break
            if f & (0x80 >> i):
                x = b[p] << 8 | b[p + 1]; p += 2
                d = (x & 0xFFF) + 1
                for _ in range((x >> 12) + 3):
                    o.append(o[-d])
            else:
                o.append(b[p]); p += 1
    return bytes(o)
