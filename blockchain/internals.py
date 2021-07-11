# June 25th 2021
# Basic Blockchain internals
# Praveer Nidamaluri
# Based on tutorial available in:
#   https://hackernoon.com/learn-blockchains-by-building-one-117428612f46

# Standard library imports
from typing import Tuple, List, Optional, Dict, Any, Set, Callable, Collection
from collections import OrderedDict
from dataclasses import dataclass, asdict
from time import time
import json
from hashlib import sha256
from urllib.parse import urlparse
import requests


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
    # Confirm each block contains the hash of the previous block
    # Confirm that the proof of a block is correct (and linked to the
    # previous block's proof)
    for curr_block, next_block in zip(chain.chain[:-1], chain.chain[1:]):
        if next_block.previous_hash != curr_block.hash() or \
                not valid_proof(curr_block.proof, next_block.proof):
            return False

    # Verify the indices of each block are correct
    for i, block in enumerate(chain.chain):
        if block.index != i:
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
        # Copy dict to ensure that the input object is not changed in
        # subsequent operations
        block_dict = block_dict.copy()
        # Ensure the minimum required keys are in the Block dictionary
        if any([key not in block_dict.keys()
                for key in ('index', 'timestamp', 'proof')]):
            raise ValueError("Insufficient information to define Block.")

        # Convert all the transaction dictionaries into Transaction
        # objects
        elif 'transactions' in block_dict.keys() and \
                block_dict['transactions'] is not None:
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
        # TODO: Add transaction verification methods. Add custom transaction
        #   exceptions that are raised here and addressed downstream.

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

    def is_valid(self) -> bool:
        """Verify that Blockchain is valid."""
        return valid_chain(self, self.valid_proof)

    def resolve_chain_conflict(self, chains: List['Blockchain']) -> bool:
        """Compare blockchain against other blockchains and resolve any
        conflicts by converting chain to the longest valid blockchain. Returns
        True if the blockchain has been redefined. Else, returns False."""
        # TODO: Update function to raise errors if the valid_proof methods are
        #   different between blockchains.
        valid_longer_chains = [
            x for x in chains if all([
                x.valid_proof == self.valid_proof,
                len(x) > len(self),
                x.is_valid(),
            ])
        ]
        if valid_longer_chains:
            self._chain = max(valid_longer_chains, key=len).chain
            return True
        return False

    def list_of_dicts(self) -> List[Dict[str, Any]]:
        """Output entire Blockchain as a list of Blocks as dictionaries.
        Intended for json outputs."""
        return [block.dict() for block in self._chain]

    def __len__(self) -> int:
        """Length of blockchain (i.e. total number of blocks, including the
        genesis block."""
        return len(self._chain)

    def __str__(self):
        """Custom string representation of blockchain and blocks."""
        string = ",\n".join([str(block) for block in self.chain])
        return f"[{string}]"

    def __eq__(self, other: 'Blockchain') -> bool:
        """A blockchain is equal to another blockchain if all Blocks
        are equal and the proof of work method is identical"""
        return (
                self.valid_proof == other.valid_proof and
                all([b1 == b2 for b1, b2 in zip(self.chain, other.chain)])
        )

    @classmethod
    def from_list_of_dicts(
            cls, chain_lst: List[Dict[str, Any]],
            valid_proof: Callable[[int, int], bool] = valid_four_zeros_proof,
    ) -> 'Blockchain':
        """Creates a Blockchain from a list of dictionaries (typical json
        format). Raises an InvalidBlockchainError if the chain is invalid."""
        new_blockchain = cls(valid_proof=valid_proof)
        new_blockchain._chain = [
            Block.from_dict(block_dict) for block_dict in chain_lst
        ]
        if new_blockchain.is_valid():
            return new_blockchain
        else:
            raise InvalidBlockchainError(new_blockchain)


# Class dealing with network interactions for Blockchain
class BlockchainNode:
    """Class that holds a Blockchain and controls networking behaviour,
     including keeping track of all server nodes holding the blockchain."""

    def __init__(self, node: str, blockchain: Blockchain):
        self.node: str = node
        self._nodes: Set[str] = {self.node}
        self.blockchain: Blockchain = blockchain

    @property
    def nodes(self):
        return self._nodes

    def register_node(self, address: str) -> None:
        """Add a new node to the network."""
        # TODO: check node validity
        self._nodes.add(urlparse(address).netloc)

    def resolve_conflicts(self):
        pass

    @staticmethod
    def get_raw_blockchain_from_node(node: str) -> Optional[Blockchain]:
        response = requests.get(fr"http://{node}/chain")

        # Successful response:
        if response.status_code == 200:
            raw_chain = response.json()['chain']
            return raw_chain

        # Unsuccessful response
        else:
            # TODO: Add Handling logic. Eg. if the address is not a valid
            #   node, then remove from nodes list. Otherwise, try again later.
            return None


# Custom Exceptions
class InvalidProofError(Exception):
    """Raised when a block mining has been attempted with an invalid proof."""

    def __init__(self, last_proof: int, proof: int):
        message = f"The proof is invalid. hash({last_proof}, {proof})" \
                  " does not end with 4 0's."
        super().__init__(message)


class InvalidBlockchainError(Exception):
    """Raised when a blockchain is generated from invalid data."""

    def __init__(self, invalid_blockchain: Blockchain):
        print(Blockchain)
        message = "The Blockchain is invalid."
        super().__init__(message)

        # TODO: Add information about why Blockchain is invalid

