# Unittests for blockchain using the Pytest framework

# Standard library imports
from pprint import pprint
from time import time

# Third party imports
import pytest

# Local application imports
from internals import Transaction, Block, Blockchain, InvalidProofError, \
    proof_of_work, valid_four_zeros_proof, valid_chain


class TestTransaction:
    pass


class TestBlock:

    @pytest.fixture
    def block(self) -> Block:
        transaction = Transaction("sender", recipient="rec", amount=3)
        block = Block(
            index=1,
            timestamp=time(),
            transactions=(transaction,),
            proof=100,
            previous_hash=None,
        )
        return block

    def test_from_dict(self, block):
        pprint(block)
        block_dict = block.dict()
        pprint(block_dict)
        new_block = Block.from_dict(block_dict)
        pprint(new_block)
        assert block == new_block

    def test_from_dict_error(self):
        with pytest.raises(ValueError):
            Block.from_dict({'index': 4})


class TestBlockchain:

    @pytest.fixture
    def chain1(self) -> Blockchain:
        test_chain = Blockchain()
        test_chain.new_transaction('test', 'test', 3)
        test_chain.new_block(proof_of_work(test_chain.last_block.proof))
        return test_chain

    def test_valid_chain(self, chain1):
        pprint(chain1.list_of_dicts())
        assert valid_chain(chain1) is True
        chain1._chain.append(chain1.last_block)
        pprint(chain1.list_of_dicts())
        assert valid_chain(chain1) is False
        assert valid_chain(Blockchain()) is True

    def test_new_block(self, chain1):
        with pytest.raises(InvalidProofError):
            chain1.new_block(0)
        last_proof = chain1.last_block.proof
        chain1.new_block(proof_of_work(chain1.last_block.proof))
        assert valid_four_zeros_proof(last_proof, chain1.last_block.proof)


class TestApplication:
    pass


