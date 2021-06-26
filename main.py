# June 25th 2021
# Basic Blockchain implementation
# Praveer Nidamaluri
# Based on tutorial available in:
#   https://hackernoon.com/learn-blockchains-by-building-one-117428612f46

# Import libaries
from typing import NamedTuple, Tuple
import requests


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
    transactions: Tuple[Transaction]
    proof: int
    previous_hash: str


# Blockchain class
class Blockchain:
    """Class for overall blockchain.
    Stores all blocks minded in a list."""

    def __init__(self):
        pass


if __name__ == '__main__':
    test_transaction = Transaction("sender", recipient="rec", amount=3)
    # test_transaction.sender = "me"
    print(test_transaction)
    print(type(test_transaction))
