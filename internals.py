# June 25th 2021
# Basic Blockchain internals
# Praveer Nidamaluri
# Based on tutorial available in:
#   https://hackernoon.com/learn-blockchains-by-building-one-117428612f46

# Standard library imports
from typing import Tuple, List, Optional, Dict, Any, Set, Callable
from collections import OrderedDict
from dataclasses import dataclass, asdict
from time import time
import json
from hashlib import sha256


# Proof of work functions
def valid_four_zeros_proof(last_proof: int, proof: int):
    """Validate the proof. I.e. does hash(last_proof*proof) contain
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


def proof_of_work(
        last_proof: int,
        valid_proof: Callable[[int, int], bool] = valid_four_zeros_proof,
) -> int:
    """Perform proof of work. The exact POW algorithm is input as a kwarg.


    Parameters
    ----------
    valid_proof:    func
    last_proof: int
                Previous proof

    Returns
    -------
    proof:  int
            Next proof.
    """
    proof = 0
    while not valid_proof(last_proof, proof):
        proof += 1
    return proof


def valid_chain(
        chain: 'Blockchain',
        valid_proof: Callable[[int, int], bool] = valid_four_zeros_proof,
) -> bool:
    """Check if the chain is valid. I.e. all blocks refer to the previous
    blocks' hash and all proofs are valid.

    Parameters
    ----------
    valid_proof:    Callable[[int, int], bool]
                    Proof of work function
    chain:          Blockchain
                    Blockchain to be checked.

    Returns
    -------
    Bool    True if chain is valid.
    """
    for curr_block, next_block in zip(chain.chain[:-1], chain.chain[1:]):
        if next_block.previous_hash != curr_block.hash() or \
                not valid_proof(curr_block.proof, next_block.proof):
            return False
    return True


# Transaction class
@dataclass(frozen=True)
class Transaction:
    """Class for immutable transaction details."""
    sender: str
    recipient: str
    amount: float


# Block class
@dataclass(frozen=True)
class Block:
    """Immutable class representing each block in a blockchain."""
    index: int
    timestamp: float
    proof: int
    previous_hash: Optional[str] = None
    transactions: Optional[Tuple[Transaction]] = None

    def dict(self) -> OrderedDict:
        """Convert Frozen dataclass into an Ordered Dict ---> makes it json
        serializable. The method also recursively converts any Transaction
        objects."""
        return asdict(self, dict_factory=OrderedDict)

    def hash(self) -> str:
        """Hash method to hash a block and return a sha256 hex str."""
        block_str = json.dumps(self.dict()).encode()
        return sha256(block_str).hexdigest()

    @classmethod
    def from_dict(cls, block_dict: Dict) -> 'Block':
        """Make a Block from a dictionary of values. Assumes the Transactions
         are also in dictionary format. Useful when building a
        Block from json outputs.

        Returns
        -------
        Block   Returns a block object with the correct data read from a dict.
        """

        # Ensure the minimum required keys are in the Block dictionary
        if any([key not in block_dict.keys()
                for key in ('index', 'timestamp', 'proof')]):
            raise ValueError("Insufficient information to define Block.")

        # Convert all the transaction dictionaries into Transaction
        # objects
        elif 'transactions' in block_dict.keys():
            block_dict['transactions'] = tuple([
                Transaction(**x) for x in block_dict['transactions']
            ])

        # Instantiate a new block using the provided keywords
        return cls(**block_dict)


# Blockchain class
class Blockchain:
    """Class for overall blockchain. Stores all blocks mined in a list starting
    from an initial genesis block. Keeps track of new transactions not placed
    in a block yet. Makes new blocks and adds to the change."""

    def __init__(
            self,
            valid_proof: Callable[[int, int], bool] = valid_four_zeros_proof,
    ) -> None:
        self.valid_proof = valid_proof
        self.unconfirmed_transactions: List[Transaction] = []
        genesis_block = Block(
            index=0,
            timestamp=time(),
            proof=100,
        )
        self._chain: List[Block] = [genesis_block]

    @property
    def chain(self) -> List[Block]:
        """Get the entire chain."""
        return self._chain

    @property
    def last_block(self) -> Block:
        """Get the most recent mined block (last on chain)"""
        return self._chain[-1]

    def new_transaction(self, sender: str, recipient: str,
                        amount: float) -> int:
        """Adds a new transactions to the list of transactions.
        Returns the index of the block that will contain the transaction."""
        self.unconfirmed_transactions.append(Transaction(
            sender, recipient, amount,
        ))
        return len(self._chain)

    def new_block(self, proof: int) -> Block:
        """Creates a new block and adds it to the chain."""
        if not self.valid_proof(self.last_block.proof, proof):
            raise InvalidProofError(self.last_block.proof, proof)
        self._chain.append(Block(
            index=len(self),
            timestamp=time(),
            transactions=tuple(self.unconfirmed_transactions),
            proof=proof,
            previous_hash=self.last_block.hash(),
        ))
        self.unconfirmed_transactions: List[Transaction] = []
        return self.last_block

    def list_of_dicts(self) -> List[Dict[str, Any]]:
        """Output entire Blockchain as a list of Blocks as dictionaries.
        Intended for json outputs."""
        return [block.dict() for block in self._chain]

    def __len__(self) -> int:
        """Length of blockchain (i.e. total number of blocks, including the
        genesis block."""
        return len(self._chain)


# Class dealing with network interactions for Blockchain
class BlockchainNetwork:
    """Class that holds a Blockchain and controls networking behaviour,
     including keeping track of all server nodes holding the blockchain."""

    def __init__(self, node: str, blockchain: Blockchain):
        self.node: str = node
        self._nodes: Set[str] = {self.node}
        self.blockchain: Blockchain = blockchain

    @property
    def nodes(self):
        return self._nodes

    def register_node(self, new_node: str) -> None:
        """Add a new node to the network."""
        self._nodes.add(new_node)


# Custom Exceptions
class InvalidProofError(Exception):
    """Raised when a block mining has been attempted with an invalid proof."""

    def __init__(self, last_proof, proof):
        message = "The proof is invalid. hash(last_proof, proof)" \
                  " does not end with 4 0's."
        super().__init__(message)
