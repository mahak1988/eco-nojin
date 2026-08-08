"""
CRYSTALS-Kyber (ML-KEM) — Educational skeleton, NIST FIPS 203
NOT for production. Use liboqs / official libs in real systems.
Manifest §4.3  |  apps/shared_core/pqc/kyber.py
"""
from __future__ import annotations
import hashlib, os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np

@dataclass(frozen=True)
class KyberParams:
    name: str; n: int; k: int; q: int; eta1: int; eta2: int; du: int; dv: int; security_level: int

KYBER512 = KyberParams("Kyber512", 256, 2, 3329, 3, 2, 10, 4, 1)
KYBER768 = KyberParams("Kyber768", 256, 3, 3329, 2, 2, 10, 4, 3)
KYBER1024 = KyberParams("Kyber1024", 256, 4, 3329, 2, 2, 11, 5, 5)

def poly_add(a, b, q): return (a + b) % q
def poly_sub(a, b, q): return (a - b) % q

def poly_mul(a, b, q, n):
    c = np.zeros(n, dtype=np.int64)
    for i in range(n):
        for j in range(n):
            coeff = int(a[i]) * int(b[j])
            if i + j < n: c[i+j] = (c[i+j] + coeff) % q
            else: c[i+j-n] = (c[i+j-n] - coeff) % q
    return c

def cbd(noise: bytes, eta: int, n: int) -> np.ndarray:
    coeffs = np.zeros(n, dtype=np.int64)
    while len(noise) * 8 < n * 2 * eta:
        noise += hashlib.sha3_256(noise).digest()
    bit_idx = 0
    for i in range(n):
        a = b = 0
        for _ in range(eta):
            a += (noise[bit_idx // 8] >> (bit_idx % 8)) & 1; bit_idx += 1
            b += (noise[bit_idx // 8] >> (bit_idx % 8)) & 1; bit_idx += 1
        coeffs[i] = a - b
    return coeffs

def compress(x, d, q): return np.round(((1 << d) / q) * x).astype(np.int64) % (1 << d)
def decompress(x, d, q): return np.round((q / (1 << d)) * x).astype(np.int64) % q

class KyberKEM:
    """keygen / encaps / decaps — educational reference."""
    def __init__(self, params: KyberParams = KYBER768):
        self.p = params

    def _noise(self, eta, seed=None):
        return cbd(seed or os.urandom(32), eta, self.p.n)

    def keygen(self) -> Tuple[bytes, bytes]:
        p = self.p
        seed_A = os.urandom(32)
        rng = np.random.RandomState(int.from_bytes(seed_A[:4], "little"))
        A = [[rng.randint(0, p.q, size=p.n).astype(np.int64) for _ in range(p.k)] for _ in range(p.k)]
        s = [self._noise(p.eta1) for _ in range(p.k)]
        e = [self._noise(p.eta1) for _ in range(p.k)]
        t = []
        for i in range(p.k):
            acc = np.zeros(p.n, dtype=np.int64)
            for j in range(p.k):
                acc = poly_add(acc, poly_mul(A[i][j], s[j], p.q, p.n), p.q)
            t.append(poly_add(acc, e[i], p.q))
        pk = seed_A + b"".join(x.astype(np.int16).tobytes() for x in t)
        sk = b"".join(x.astype(np.int16).tobytes() for x in s) + pk
        self._A, self._s, self._t = A, s, t
        return pk, sk

    def encaps(self, pk: bytes) -> Tuple[bytes, bytes]:
        p = self.p
        seed_A, offset = pk[:32], 32
        t = []
        for _ in range(p.k):
            t.append(np.frombuffer(pk[offset:offset+p.n*2], dtype=np.int16).astype(np.int64))
            offset += p.n * 2
        rng = np.random.RandomState(int.from_bytes(seed_A[:4], "little"))
        A = [[rng.randint(0, p.q, size=p.n).astype(np.int64) for _ in range(p.k)] for _ in range(p.k)]
        m = os.urandom(32)
        r = [self._noise(p.eta1, hashlib.sha3_256(m + bytes([i])).digest()) for i in range(p.k)]
        e1 = [self._noise(p.eta2) for _ in range(p.k)]
        e2 = self._noise(p.eta2)
        u = []
        for i in range(p.k):
            acc = np.zeros(p.n, dtype=np.int64)
            for j in range(p.k):
                acc = poly_add(acc, poly_mul(A[j][i], r[j], p.q, p.n), p.q)
            u.append(compress(poly_add(acc, e1[i], p.q), p.du, p.q))
        m_poly = np.zeros(p.n, dtype=np.int64)
        for i, byte in enumerate(m):
            for b in range(8):
                if i*8+b < p.n: m_poly[i*8+b] = ((byte >> b) & 1) * (p.q // 2)
        acc = np.zeros(p.n, dtype=np.int64)
        for j in range(p.k):
            acc = poly_add(acc, poly_mul(t[j], r[j], p.q, p.n), p.q)
        v = compress(poly_add(poly_add(acc, e2, p.q), m_poly, p.q), p.dv, p.q)
        ct = b"".join(x.astype(np.int16).tobytes() for x in u) + v.astype(np.int16).tobytes()
        return ct, hashlib.sha3_256(m + ct).digest()

    def decaps(self, sk: bytes, ct: bytes) -> bytes:
        p = self.p
        s, offset = [], 0
        for _ in range(p.k):
            s.append(np.frombuffer(sk[offset:offset+p.n*2], dtype=np.int16).astype(np.int64))
            offset += p.n * 2
        u, offset = [], 0
        for _ in range(p.k):
            u.append(decompress(np.frombuffer(ct[offset:offset+p.n*2], dtype=np.int16).astype(np.int64), p.du, p.q))
            offset += p.n * 2
        v = decompress(np.frombuffer(ct[offset:offset+p.n*2], dtype=np.int16).astype(np.int64), p.dv, p.q)
        acc = np.zeros(p.n, dtype=np.int64)
        for j in range(p.k):
            acc = poly_add(acc, poly_mul(s[j], u[j], p.q, p.n), p.q)
        m_poly = poly_sub(v, acc, p.q)
        m = bytearray(32)
        for i in range(min(32, p.n // 8)):
            byte = 0
            for b in range(8):
                if abs(int(m_poly[i*8+b]) - p.q//2) < abs(int(m_poly[i*8+b])):
                    byte |= 1 << b
            m[i] = byte
        return hashlib.sha3_256(bytes(m) + ct).digest()

def demo_kyber(params: KyberParams = KYBER768) -> Dict:
    kem = KyberKEM(params)
    pk, sk = kem.keygen()
    ct, ss_enc = kem.encaps(pk)
    ss_dec = kem.decaps(sk, ct)
    return {"params": params.name, "pk_len": len(pk), "sk_len": len(sk),
            "ct_len": len(ct), "ss_match": ss_enc == ss_dec, "ss_hex": ss_enc.hex()[:32]+"…"}

if __name__ == "__main__":
    print("=== Kyber (ML-KEM) self-test ===")
    for p in (KYBER512, KYBER768):
        out = demo_kyber(p)
        print(f"  {out['params']}: pk={out['pk_len']}B ct={out['ct_len']}B match={out['ss_match']}")
    print("OK")
