# Secure Blockchain Banking

A Python mini-project that demonstrates **secure money transactions using blockchain technology**.

## Features

- Wallet identities using large-prime public/private key pairs (Schnorr-style signatures).
- Digitally signed transactions.
- Verification of sender signatures before transactions are accepted.
- Proof-of-work mining.
- Block and chain hashing for tamper evidence.
- Balance calculation from on-chain transfer history.

## Project structure

- `src/wallet.py` – key generation, signing, and verification.
- `src/blockchain.py` – transaction model, block model, chain logic.
- `src/main.py` – runnable demo flow.
- `tests/test_blockchain.py` – unit tests for integrity and transaction security.

## Quick start

```bash
python3 src/main.py
```

## Run tests

```bash
python3 -m unittest discover -s tests -v
```

## Notes

This project is intentionally compact for learning and final-year-project prototyping. For production usage, add persistent storage, peer-to-peer networking, replay protection with account nonces, stronger consensus design, and auditing.
