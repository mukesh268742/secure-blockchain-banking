"""Demo run for secure blockchain banking transactions."""

from __future__ import annotations

import time

from blockchain import Blockchain, Transaction
from wallet import Wallet


def build_signed_transaction(sender: Wallet, recipient: Wallet, amount: float) -> Transaction:
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


def main() -> None:
    chain = Blockchain(difficulty=3)

    bank = Wallet.create()
    alice = Wallet.create()
    bob = Wallet.create()

    # Fund Alice from initial mining rewards.
    chain.mine_pending_transactions(bank.address)
    funding_tx = build_signed_transaction(bank, alice, 3.0)
    chain.add_transaction(funding_tx)
    chain.mine_pending_transactions(bank.address)

    payment = build_signed_transaction(alice, bob, 1.25)
    chain.add_transaction(payment)
    mined = chain.mine_pending_transactions(bank.address)

    print(f"Mined block #{mined.index} with hash {mined.hash}")
    print(f"Alice balance: {chain.get_balance(alice.address)}")
    print(f"Bob balance: {chain.get_balance(bob.address)}")
    print(f"Bank balance: {chain.get_balance(bank.address)}")
    print(f"Chain valid: {chain.is_chain_valid()}")


if __name__ == "__main__":
    main()
