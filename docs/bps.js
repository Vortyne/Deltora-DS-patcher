// BPS patching (the beat format), in the browser. Mirrors builder/bps.py's apply().
"use strict";

const BPS = (() => {
  const CRC_TABLE = (() => {
    const t = new Uint32Array(256);
    for (let n = 0; n < 256; n++) {
      let c = n;
      for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
      t[n] = c >>> 0;
    }
    return t;
  })();

  function crc32(bytes, start = 0, end = bytes.length) {
    let c = 0xffffffff;
    for (let i = start; i < end; i++) c = CRC_TABLE[(c ^ bytes[i]) & 0xff] ^ (c >>> 8);
    return (c ^ 0xffffffff) >>> 0;
  }

  function u32(bytes, at) {
    return (bytes[at] | bytes[at + 1] << 8 | bytes[at + 2] << 16 | bytes[at + 3] << 24) >>> 0;
  }

  // source, patch: Uint8Array. Returns the patched Uint8Array, or throws.
  function apply(source, patch) {
    if (String.fromCharCode(...patch.subarray(0, 4)) !== "BPS1") throw new Error("Not a BPS patch.");
    if (crc32(patch, 0, patch.length - 4) !== u32(patch, patch.length - 4)) throw new Error("The patch file is damaged.");
    let p = 4;
    const varint = () => {
      let n = 0, shift = 1;
      for (;;) {
        const x = patch[p++];
        n += (x & 0x7f) * shift;
        if (x & 0x80) return n;
        shift *= 128;
        n += shift;
      }
    };
    const sourceSize = varint(), targetSize = varint(), metaSize = varint();
    p += metaSize;
    if (source.length !== sourceSize) throw new Error("The ROM is the wrong size for this patch.");
    const target = new Uint8Array(targetSize);
    const end = patch.length - 12;
    let out = 0, sourceRel = 0, targetRel = 0;
    while (p < end) {
      const x = varint(), length = Math.floor(x / 4) + 1;
      switch (x & 3) {
        case 0:   // SourceRead: the same place in the original
          target.set(source.subarray(out, out + length), out);
          break;
        case 1:   // TargetRead: new bytes in the patch
          target.set(patch.subarray(p, p + length), out);
          p += length;
          break;
        case 2: { // SourceCopy: from elsewhere in the original
          const d = varint();
          sourceRel += d & 1 ? -Math.floor(d / 2) : Math.floor(d / 2);
          target.set(source.subarray(sourceRel, sourceRel + length), out);
          sourceRel += length;
          break;
        }
        default: { // TargetCopy: from earlier in the result (may overlap, so byte by byte)
          const d = varint();
          targetRel += d & 1 ? -Math.floor(d / 2) : Math.floor(d / 2);
          for (let i = 0; i < length; i++) target[out + i] = target[targetRel++];
        }
      }
      out += length;
    }
    if (crc32(target) !== u32(patch, patch.length - 8)) throw new Error("The patched ROM didn't come out right.");
    return target;
  }

  return { apply, crc32 };
})();

if (typeof module !== "undefined") module.exports = BPS;
