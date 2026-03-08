"""Wallet and signature utilities for the secure blockchain banking demo.

Implements a Schnorr-style signature scheme over a large safe-prime field
using only Python standard library primitives.
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass


# RFC 3526 - 2048-bit MODP Group prime (Group 14).
P = int(
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E08"
    "8A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD"
    "3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E"
    "7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899F"
    "A5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF05"
    "98DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C"
    "62F356208552BB9ED529077096966D670C354E4ABC9804F174"
    "6C08CA237327FFFFFFFFFFFFFFFF",
    16,
)
G = 2
Q = (P - 1) // 2


@dataclass(frozen=True)
class Signature:
    e: int
    s: int

    def encode(self) -> str:
        return f"{self.e:x}:{self.s:x}"

    @staticmethod
    def decode(value: str) -> "Signature":
        e_hex, s_hex = value.split(":", maxsplit=1)
        return Signature(e=int(e_hex, 16), s=int(s_hex, 16))


@dataclass
class Wallet:
    private_key: int
    public_key: int

    @staticmethod
    def create() -> "Wallet":
        private_key = secrets.randbelow(Q - 1) + 1
        public_key = pow(G, private_key, P)
        return Wallet(private_key=private_key, public_key=public_key)

    @property
    def address(self) -> str:
        return f"0x{self.public_key:x}"

    def sign(self, message: str) -> Signature:
        nonce = secrets.randbelow(Q - 1) + 1
        r = pow(G, nonce, P)
        e = _challenge(r, message)
        s = (nonce + self.private_key * e) % Q
        return Signature(e=e, s=s)


def verify_signature(public_key: int, message: str, signature: Signature) -> bool:
    if not (0 < public_key < P and 0 <= signature.e < Q and 0 <= signature.s < Q):
        return False

    y_inv = pow(public_key, P - 2, P)
    r_prime = (pow(G, signature.s, P) * pow(y_inv, signature.e, P)) % P
    expected = _challenge(r_prime, message)
    return expected == signature.e


def _challenge(r_value: int, message: str) -> int:
    digest = hashlib.sha256(f"{r_value}|{message}".encode("utf-8")).hexdigest()
    return int(digest, 16) % Q
