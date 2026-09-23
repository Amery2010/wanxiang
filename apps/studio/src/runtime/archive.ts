export type ArchiveFile = [string, string | Uint8Array<ArrayBuffer>];
const crcTable = (() => {
  const t = new Uint32Array(256);
  for (let i = 0; i < 256; i++) {
    let c = i;
    for (let j = 0; j < 8; j++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    t[i] = c >>> 0;
  }
  return t;
})();
function crc32(a: Uint8Array) {
  let c = 0xffffffff;
  for (const x of a) c = crcTable[(c ^ x) & 255] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}
// SHA-256 on ordinary typed arrays; works in file:// pages without secure-context APIs.
export function sha256Bytes(input: Uint8Array | string) {
  const bytes =
    typeof input === "string" ? new TextEncoder().encode(input) : input;
  const K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1,
    0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
    0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
    0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
    0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
    0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
  ];
  const n = Math.ceil((bytes.length + 9) / 64) * 64,
    p = new Uint8Array(n);
  p.set(bytes);
  p[bytes.length] = 128;
  const view = new DataView(p.buffer);
  view.setUint32(n - 8, Math.floor(bytes.length / 0x20000000));
  view.setUint32(n - 4, (bytes.length * 8) >>> 0);
  const h = new Uint32Array([
      0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c,
      0x1f83d9ab, 0x5be0cd19,
    ]),
    w = new Uint32Array(64),
    rr = (x: number, k: number) => (x >>> k) | (x << (32 - k));
  for (let off = 0; off < n; off += 64) {
    for (let i = 0; i < 16; i++) w[i] = view.getUint32(off + i * 4);
    for (let i = 16; i < 64; i++) {
      const x = w[i - 15],
        y = w[i - 2];
      w[i] =
        (w[i - 16] +
          (rr(x, 7) ^ rr(x, 18) ^ (x >>> 3)) +
          w[i - 7] +
          (rr(y, 17) ^ rr(y, 19) ^ (y >>> 10))) >>>
        0;
    }
    let [a, b, c, d, e, f, g, j] = h;
    for (let i = 0; i < 64; i++) {
      const t1 =
          (j +
            (rr(e, 6) ^ rr(e, 11) ^ rr(e, 25)) +
            ((e & f) ^ (~e & g)) +
            K[i] +
            w[i]) >>>
          0,
        t2 =
          ((rr(a, 2) ^ rr(a, 13) ^ rr(a, 22)) +
            ((a & b) ^ (a & c) ^ (b & c))) >>>
          0;
      j = g;
      g = f;
      f = e;
      e = (d + t1) >>> 0;
      d = c;
      c = b;
      b = a;
      a = (t1 + t2) >>> 0;
    }
    const v = [a, b, c, d, e, f, g, j];
    for (let i = 0; i < 8; i++) h[i] = (h[i] + v[i]) >>> 0;
  }
  return [...h].map((x) => x.toString(16).padStart(8, "0")).join("");
}

export function closedManifest(files: ArchiveFile[]) {
  return JSON.stringify(
    {
      schema: "wx.package/1.0",
      closed_roster: true,
      files: Object.fromEntries(
        files.map(([name, data]) => {
          const b =
            typeof data === "string" ? new TextEncoder().encode(data) : data;
          return [name, { sha256: sha256Bytes(b), bytes: b.length }];
        }),
      ),
    },
    null,
    2,
  );
}

export function zipStore(files: ArchiveFile[]) {
  const enc = new TextEncoder(),
    parts: Uint8Array<ArrayBuffer>[] = [],
    central: Uint8Array<ArrayBuffer>[] = [];
  let offset = 0;
  for (const [name, data] of files) {
    const n = enc.encode(name),
      a = typeof data === "string" ? enc.encode(data) : data;
    const crc = crc32(a),
      h = new Uint8Array(30 + n.length),
      v = new DataView(h.buffer);
    v.setUint32(0, 0x04034b50, true);
    v.setUint16(4, 20, true);
    v.setUint16(6, 0x800, true);
    v.setUint32(14, crc, true);
    v.setUint32(18, a.length, true);
    v.setUint32(22, a.length, true);
    v.setUint16(26, n.length, true);
    h.set(n, 30);
    parts.push(h, a);
    const c = new Uint8Array(46 + n.length),
      d = new DataView(c.buffer);
    d.setUint32(0, 0x02014b50, true);
    d.setUint16(4, 20, true);
    d.setUint16(6, 20, true);
    d.setUint16(8, 0x800, true);
    d.setUint32(16, crc, true);
    d.setUint32(20, a.length, true);
    d.setUint32(24, a.length, true);
    d.setUint16(28, n.length, true);
    d.setUint32(42, offset, true);
    c.set(n, 46);
    central.push(c);
    offset += h.length + a.length;
  }
  const size = central.reduce((s, a) => s + a.length, 0),
    end = new Uint8Array(22),
    e = new DataView(end.buffer);
  e.setUint32(0, 0x06054b50, true);
  e.setUint16(8, files.length, true);
  e.setUint16(10, files.length, true);
  e.setUint32(12, size, true);
  e.setUint32(16, offset, true);
  return new Blob([...parts, ...central, end], { type: "application/zip" });
}

export function from64(s: string): Uint8Array<ArrayBuffer> {
  const str = atob(s),
    a = new Uint8Array(str.length);
  for (let i = 0; i < str.length; i++) a[i] = str.charCodeAt(i);
  return a;
}
export function to64(buffer: ArrayBuffer): string {
  const a = new Uint8Array(buffer);
  let s = "";
  for (let i = 0; i < a.length; i += 8192)
    s += String.fromCharCode(...a.subarray(i, i + 8192));
  return btoa(s);
}
