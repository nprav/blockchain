# June 25th 2021
# Basic Blockchain implementation
# Praveer Nidamaluri
# Based on tutorial available in:
#   https://hackernoon.com/learn-blockchains-by-building-one-117428612f46

# Import libaries
from typing import NamedTuple, Tuple, List, Optional
from time import time
import requests
import json
from hashlib import sha256
from uuid import uuid4


# Transaction class
class Transaction(NamedTuple):
    """Class for immutable transaction details."""
    # TODO: implement input type checks
    sender: str
    recipient: str
    amount: float


# Block class
class Block(NamedTuple):
    """Immutable class representing each block in a blockchain."""
    # TODO: implement input type checks
    index: int
    timestamp: float
    transactions: Optional[Tuple[Transaction]]
    proof: int
    previous_hash: Optional[str]


# Blockchain class
class Blockchain:
    """Class for overall blockchain.
    Stores all blocks mined in a list."""

    def __init__(self) -> None:
        self.unconfirmed_transactions: List[Transaction] = []
        genesis_block = Block(
            index=0,
            timestamp=time(),
            transactions=None,
            proof=0,
            previous_hash=None,
        )
        self.chain: List[Block] = [genesis_block]

    def new_block(self, proof: int) -> Block:
        """Creates a new block and adds it to the chain."""
        self.chain.append(Block(
            index=len(self),
            timestamp=time(),
            transactions=tuple(self.unconfirmed_transactions),
            proof=proof,
            previous_hash=self.hash(self.chain[-1]),
        ))
        self.unconfirmed_transactions = []
        return self.chain[-1]

    def new_transaction(self, sender: str, recipient: str,
                        amount: float) -> int:
        """Adds a new transactions to the list of transactions.
        Returns the index of the block that will contains the transaction."""
        self.unconfirmed_transactions.append(Transaction(
            sender, recipient, amount,
        ))
        return len(self.chain)

    def __len__(self) -> int:
        """Length of blockchain (i.e. total number of blocks, including the
        genesis block."""
        return len(self.chain)

    @staticmethod
    def hash(block: Block) -> str:
        """Hash method to hash a block."""
        return ""

    @property
    def last_block(self) -> Block:
        """Get the most recent mined block (last on chain)"""
        return self.chain[-1]

    def proof_of_work(self, last_proof: int) -> int:
        """Simple Proof of Work algorithm.:
            -   Find a number p' such that hash(p*p') contains 4 leading 0s
                where p is the previous p'.
            -   p is the previous proof, and p' is the new proof.

        Parameters
        ----------
        last_proof: int
                    Previous proof

        Returns
        -------
        proof:  int
                Next proof.
        """
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof: int, proof: int):
        """Validate the proof. I.e. does hash(last_proof, proof) contain
        4 leading zeros.

        Parameters
        ----------
        last_proof: int
                    Previous proof
        proof:      int
                    Current proof

        Returns
        -------
        bool        True if correct proof, False if not.
        """
        guess_utf = f'{last_proof}{proof}'.encode()
        guess_hash = sha256(guess_utf).hexdigest()
        return guess_hash[:4] == "0000"


if __name__ == '__main__':
    test_transaction = Transaction("sender", recipient="rec", amount=3)
    # test_transaction.sender = "me"
    print(test_transaction)
    print(type(test_transaction))

    test_chain = Blockchain()
    test_chain.new_transaction('test', 'test', 3)
    print(test_chain.unconfirmed_transactions)
    test_chain.new_block(4)
    print(test_chain.unconfirmed_transactions)
    print(test_chain.chain)
    print(test_chain.last_block)
