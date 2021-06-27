# June 25th 2021
# Basic Blockchain implementation
# Praveer Nidamaluri
# Based on tutorial available in:
#   https://hackernoon.com/learn-blockchains-by-building-one-117428612f46

# Import libaries
from typing import Tuple, List, Optional, Dict, Any
from collections import OrderedDict
from dataclasses import dataclass, asdict
from time import time
import json
from hashlib import sha256
from uuid import uuid4
from flask import Flask, jsonify


# Transaction class
@dataclass(frozen=True)
class Transaction:
    """Class for immutable transaction details."""
    # TODO: implement input type checks
    sender: str
    recipient: str
    amount: float


# Block class
@dataclass(frozen=True)
class Block:
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
            proof=100,
            previous_hash=None,
        )
        self._chain: List[Block] = [genesis_block]

    def new_block(self, proof: int) -> Block:
        """Creates a new block and adds it to the chain."""
        self._chain.append(Block(
            index=len(self),
            timestamp=time(),
            transactions=tuple(self.unconfirmed_transactions),
            proof=proof,
            previous_hash=self.hash(self._chain[-1]),
        ))
        self.unconfirmed_transactions = []
        return self._chain[-1]

    def new_transaction(self, sender: str, recipient: str,
                        amount: float) -> int:
        """Adds a new transactions to the list of transactions.
        Returns the index of the block that will contains the transaction."""
        self.unconfirmed_transactions.append(Transaction(
            sender, recipient, amount,
        ))
        return len(self._chain)

    def __len__(self) -> int:
        """Length of blockchain (i.e. total number of blocks, including the
        genesis block."""
        return len(self._chain)

    @staticmethod
    def hash(block: Block) -> str:
        """Hash method to hash a block and return a str.
        """
        block_str = json.dumps(
            asdict(block, dict_factory=OrderedDict)
        ).encode()
        return sha256(block_str).hexdigest()

    @property
    def last_block(self) -> Block:
        """Get the most recent mined block (last on chain)"""
        return self._chain[-1]

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

    def show_chain(self) -> List[Dict[str, Any]]:
        """Output entire Blockchain with Blocks as dictionaries.
        Intended for json outputs."""
        return [asdict(block, dict_factory=OrderedDict)
                for block in self._chain]


def create_blockchain_application() -> Flask:
    """FUnction that contains the networking setup for the
    Blockchain"""

    # Flask app instantation
    app = Flask(__name__)
    blockchain = Blockchain()

    # Globally unique address for node
    node_id = str(uuid4()).replace('-', '')

    @app.route('/mine', methods=['GET'])
    def mine() -> str:
        return "We'll mine a new block."

    @app.route('/transactions/new', methods=['POST'])
    def new_transaction() -> str:
        return "We'll add a new transaction."

    @app.route('/chain', methods=['GET'])
    def full_chain() -> [str, int]:
        response = {
            'chain': blockchain.show_chain(),
            'length': len(blockchain),
        }
        return jsonify(response), 200

    app.run(host='0.0.0.0', port=5000)

    return app


if __name__ == '__main__':

    # Test Functions
    test_transaction = Transaction("sender", recipient="rec", amount=3)
    # test_transaction.sender = "me"
    print(test_transaction)
    print(type(test_transaction))

    test_chain = Blockchain()
    test_chain.new_transaction('test', 'test', 3)
    print(test_chain.unconfirmed_transactions)
    test_chain.new_block(4)
    print(test_chain.unconfirmed_transactions)
    print(test_chain.show_chain())
    print(test_chain.last_block)
    print(test_chain.hash(test_chain.last_block))
    dump = json.dumps(asdict(test_chain.last_block))
    print(dump)
    print(json.loads(dump))
    print(test_chain.proof_of_work(test_chain.last_block.proof))

    # Main Flask Functions
    app = create_blockchain_application()