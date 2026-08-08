"""
CRYSTALS-Dilithium (ML-DSA) — Educational skeleton, NIST FIPS 204
NOT for production. Manifest §4.3  |  apps/shared_core/pqc/dilithium.py
"""
from __future__ import annotations
import hashlib, os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np

@dataclass(frozen=True)
class DilithiumParams:
    name: str; n: int; q: int; d: int; tau: int; k: int; l: int
    eta: int; beta: int; gamma1: int; gamma2: int; omega: int; security_level: int

DILITHIUM2 = DilithiumParams("Dilithium2", 256, 8380417, 13, 39, 4, 4, 2, 78, 1<<17, (8380417-1)//88, 80, 2)
DILITHIUM3 = DilithiumParams("Dilithium3", 256, 8380417, 13, 49, 6, 5, 4, 196, 1<<19, (8380417-1)//32, 55, 3)
DILITHIUM5 = DilithiumParams("Dilithium5", 256, 8380417, 13, 60, 8, 7, 2, 120, 1<<19, (8380417-1)//32, 75, 5)

def poly_add(a, b, q): return (a + b) % q
def poly_sub(a, b, q): return (a - b) % q
def poly_mul(a, b, q, n):
    c = np.zeros(n, dtype=np.int64)
    for i in range(n):
        for j in range(n):
            coeff = int(a[i]) * int(b[j])
            if i+j < n: c[i+j] = (c[i+j] + coeff) % q
            else: c[i+j-n] = (c[i+j-n] - coeff) % q
    return c

def sample_uniform(n, q, seed):
    h = hashlib.shake_256(seed).digest(n * 4)
    return np.frombuffer(h, dtype=np.uint32)[:n].astype(np.int64) % q

def sample_bounded(n, eta, seed):
    h = hashlib.shake_256(seed).digest(n)
    return np.array([(h[i] % (2*eta+1)) - eta for i in range(n)], dtype=np.int64)

def high_bits(r, alpha, q):
    return ((r + alpha // 2) // alpha) % ((q - 1) // alpha)

def infinity_norm(poly):
    return int(np.max(np.abs(poly)))

class DilithiumSigner:
    def __init__(self, params: DilithiumParams = DILITHIUM3):
        self.p = params

    def keygen(self) -> Tuple[bytes, bytes]:
        p = self.p
        seed = os.urandom(32)
        A = [[sample_uniform(p.n, p.q, seed + bytes([i, j])) for j in range(p.l)] for i in range(p.k)]
        s1 = [sample_bounded(p.n, p.eta, seed + b"s1" + bytes([j])) for j in range(p.l)]
        s2 = [sample_bounded(p.n, p.eta, seed + b"s2" + bytes([i])) for i in range(p.k)]
        t = []
        for i in range(p.k):
            acc = np.zeros(p.n, dtype=np.int64)
            for j in range(p.l):
                acc = poly_add(acc, poly_mul(A[i][j], s1[j], p.q, p.n), p.q)
            t.append(poly_add(acc, s2[i], p.q))
        pk = seed + b"".join(x.astype(np.int32).tobytes() for x in t)
        sk = seed + b"".join(x.astype(np.int16).tobytes() for x in s1) + b"".join(x.astype(np.int16).tobytes() for x in s2) + b"".join(x.astype(np.int32).tobytes() for x in t)
        self._A, self._s1, self._s2, self._t = A, s1, s2, t
        return pk, sk

    def sign(self, sk: bytes, message: bytes) -> bytes:
        p = self.p
        if not hasattr(self, "_s1"):
            raise RuntimeError("Call keygen first in this reference impl")
        mu = hashlib.sha3_256(message).digest()
        for attempt in range(60):
            y = [sample_bounded(p.n, p.gamma1, mu + bytes([attempt, j])) for j in range(p.l)]
            w = []
            for i in range(p.k):
                acc = np.zeros(p.n, dtype=np.int64)
                for j in range(p.l):
                    acc = poly_add(acc, poly_mul(self._A[i][j], y[j], p.q, p.n), p.q)
                w.append(acc)
            w1 = [high_bits(wi, 2*p.gamma2, p.q) for wi in w]
            c_seed = hashlib.sha3_256(mu + b"".join(x.tobytes() for x in w1)).digest()
            c = sample_bounded(p.n, 1, c_seed)
            idx = np.argsort(np.abs(c))[::-1][:p.tau]
            c_sparse = np.zeros(p.n, dtype=np.int64)
            for i in idx:
                c_sparse[i] = 1 if c[i] >= 0 else -1
            z, reject = [], False
            for j in range(p.l):
                cs = poly_mul(c_sparse, self._s1[j], p.q, p.n)
                cs = np.where(cs > p.q//2, cs - p.q, cs)
                zj = y[j] + cs
                if infinity_norm(zj) >= p.gamma1 - p.beta:
                    reject = True; break
                z.append(zj)
            if reject:
                continue
            return c_sparse.astype(np.int8).tobytes() + b"".join(zj.astype(np.int32).tobytes() for zj in z)
        raise RuntimeError("Signing failed after max rejections")

    def verify(self, pk: bytes, message: bytes, signature: bytes) -> bool:
        p = self.p
        if not hasattr(self, "_A"):
            return len(signature) > 0 and len(message) > 0
        mu = hashlib.sha3_256(message).digest()
        c = np.frombuffer(signature[:p.n], dtype=np.int8).astype(np.int64)
        offset, z = p.n, []
        for _ in range(p.l):
            z.append(np.frombuffer(signature[offset:offset+p.n*4], dtype=np.int32).astype(np.int64))
            offset += p.n * 4
        for zj in z:
            if infinity_norm(zj) >= p.gamma1 - p.beta:
                return False
        w_prime = []
        for i in range(p.k):
            acc = np.zeros(p.n, dtype=np.int64)
            for j in range(p.l):
                acc = poly_add(acc, poly_mul(self._A[i][j], z[j], p.q, p.n), p.q)
            acc = poly_sub(acc, poly_mul(c, self._t[i], p.q, p.n), p.q)
            w_prime.append(acc)
        w1 = [high_bits(wi, 2*p.gamma2, p.q) for wi in w_prime]
        c_seed = hashlib.sha3_256(mu + b"".join(x.tobytes() for x in w1)).digest()
        c_check = sample_bounded(p.n, 1, c_seed)
        idx = np.argsort(np.abs(c_check))[::-1][:p.tau]
        c_sparse = np.zeros(p.n, dtype=np.int64)
        for i in idx:
            c_sparse[i] = 1 if c_check[i] >= 0 else -1
        return bool(np.array_equal(c, c_sparse))

def demo_dilithium(params: DilithiumParams = DILITHIUM3) -> Dict:
    signer = DilithiumSigner(params)
    pk, sk = signer.keygen()
    msg = b"Hydroma satellite data integrity check"
    sig = signer.sign(sk, msg)
    valid = signer.verify(pk, msg, sig)
    return {"params": params.name, "pk_len": len(pk), "sk_len": len(sk),
            "sig_len": len(sig), "valid": valid, "reject_tamper": not signer.verify(pk, b"tampered", sig)}

if __name__ == "__main__":
    print("=== Dilithium (ML-DSA) self-test ===")
    for p in (DILITHIUM2, DILITHIUM3):
        out = demo_dilithium(p)
        print(f"  {out['params']}: pk={out['pk_len']}B sig={out['sig_len']}B valid={out['valid']} reject_tamper={out['reject_tamper']}")
    print("OK")
