"""Core blockchain models for secure banking transactions."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Dict, List

from wallet import Signature, verify_signature


@dataclass
class Transaction:
    sender: str
    recipient: str
    amount: float
    timestamp: float
    sender_public_key: int
    signature: str

    def payload(self) -> Dict[str, float | str | int]:
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "timestamp": self.timestamp,
        }

    def message(self) -> str:
        return json.dumps(self.payload(), sort_keys=True, separators=(",", ":"))

    def is_valid(self) -> bool:
        if self.amount <= 0:
            return False
        if self.sender == self.recipient:
            return False
        if self.sender != f"0x{self.sender_public_key:x}":
            return False
        signature = Signature.decode(self.signature)
        return verify_signature(self.sender_public_key, self.message(), signature)


@dataclass
class Block:
    index: int
    previous_hash: str
    timestamp: float
    transactions: List[Transaction]
    nonce: int = 0
    hash: str = ""

    def calculate_hash(self) -> str:
        serializable = {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "transactions": [tx.payload() | {"signature": tx.signature} for tx in self.transactions],
        }
        encoded = json.dumps(serializable, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


@dataclass
class Blockchain:
    difficulty: int = 3
    mining_reward: float = 5.0
    chain: List[Block] = field(default_factory=list)
    pending_transactions: List[Transaction] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.chain:
            self.chain.append(self._create_genesis_block())

    def _create_genesis_block(self) -> Block:
        block = Block(index=0, previous_hash="0", timestamp=time.time(), transactions=[])
        block.hash = block.calculate_hash()
        return block

    @property
    def latest_block(self) -> Block:
        return self.chain[-1]

    def add_transaction(self, transaction: Transaction) -> None:
        if not transaction.is_valid():
            raise ValueError("Invalid transaction signature or payload")
        if self.get_balance(transaction.sender) < transaction.amount:
            raise ValueError("Insufficient balance")
        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self, miner_address: str) -> Block:
        reward = Transaction(
            sender="SYSTEM",
            recipient=miner_address,
            amount=self.mining_reward,
            timestamp=time.time(),
            sender_public_key=1,
            signature="0:0",
        )

        block = Block(
            index=len(self.chain),
            previous_hash=self.latest_block.hash,
            timestamp=time.time(),
            transactions=[*self.pending_transactions, reward],
        )
        self._proof_of_work(block)
        self.chain.append(block)
        self.pending_transactions = []
        return block

    def _proof_of_work(self, block: Block) -> None:
        prefix = "0" * self.difficulty
        while True:
            block.hash = block.calculate_hash()
            if block.hash.startswith(prefix):
                return
            block.nonce += 1

    def get_balance(self, address: str) -> float:
        balance = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address:
                    balance -= tx.amount
                if tx.recipient == address:
                    balance += tx.amount
        return round(balance, 8)

    def is_chain_valid(self) -> bool:
        prefix = "0" * self.difficulty
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if current.previous_hash != previous.hash:
                return False
            if current.calculate_hash() != current.hash:
                return False
            if not current.hash.startswith(prefix):
                return False
            for tx in current.transactions:
                if tx.sender == "SYSTEM":
                    continue
                if not tx.is_valid():
                    return False
        return True
