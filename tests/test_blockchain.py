from __future__ import annotations

import os
import sys
import time
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from blockchain import Blockchain, Transaction
from wallet import Wallet


class BlockchainTests(unittest.TestCase):
    def setUp(self) -> None:
        self.chain = Blockchain(difficulty=2, mining_reward=5.0)
        self.miner = Wallet.create()
        self.alice = Wallet.create()
        self.bob = Wallet.create()

    def sign_transaction(self, sender: Wallet, recipient: Wallet, amount: float) -> Transaction:
        tx = Transaction(
            sender=sender.address,
            recipient=recipient.address,
            amount=amount,
            timestamp=time.time(),
            sender_public_key=sender.public_key,
            signature="",
        )
        tx.signature = sender.sign(tx.message()).encode()
        return tx

    def test_valid_signed_transaction_is_accepted(self) -> None:
        self.chain.mine_pending_transactions(self.miner.address)
        tx = self.sign_transaction(self.miner, self.alice, 2.0)
        self.chain.add_transaction(tx)
        self.chain.mine_pending_transactions(self.miner.address)

        self.assertEqual(self.chain.get_balance(self.alice.address), 2.0)
        self.assertTrue(self.chain.is_chain_valid())

    def test_tampered_transaction_is_rejected(self) -> None:
        tx = self.sign_transaction(self.miner, self.alice, 1.0)
        tx.amount = 100.0

        with self.assertRaises(ValueError):
            self.chain.add_transaction(tx)

    def test_chain_tampering_is_detected(self) -> None:
        self.chain.mine_pending_transactions(self.miner.address)
        tx = self.sign_transaction(self.miner, self.alice, 1.0)
        self.chain.add_transaction(tx)
        self.chain.mine_pending_transactions(self.miner.address)

        self.chain.chain[1].transactions[0].amount = 999.0
        self.assertFalse(self.chain.is_chain_valid())


if __name__ == "__main__":
    unittest.main()
