# Unittests for blockchain using the Pytest framework

# Standard library imports
from pprint import pprint
from dataclasses import FrozenInstanceError
import json

# Third party imports
import pytest

# Local application imports
from blockchain.internals import *


class TestTransaction:

    def test_frozen(self):
        t = Transaction(sender='a', recipient='b', amount=10)
        with pytest.raises(FrozenInstanceError):
            t.sender = 'c'

    def test_str_amount(self):
        t = Transaction(sender='a', recipient='b', amount='39')
        assert type(t.amount) == float


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
        block_json = json.dumps(block.dict())
        pprint(block_json)
        block_dict = json.loads(block_json)
        new_block = Block.from_dict(block_dict)
        pprint(new_block)
        assert block == new_block
        block_dict['transactions'] = None
        new_block = Block.from_dict(block_dict)
        pprint(new_block)
        assert new_block.transactions is None

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

    @pytest.fixture
    def chain_lst(self) -> List[Blockchain]:
        chains = [
            Blockchain(valid_proof=valid_four_zeros_proof) for i in range(4)
        ]
        for i, chain in enumerate(chains):
            for j in range(i):
                chain.new_block(proof_of_work(chain.last_block.proof))
        return chains

    @pytest.fixture
    def invalid_chain_lst(self) -> List[Blockchain]:
        invalid_chains = [
            Blockchain(valid_proof=valid_four_zeros_proof) for i in range(4)
        ]
        for i, chain in enumerate(invalid_chains):
            for j in range(i):
                chain._chain.append(chain.last_block)
        return invalid_chains

    def test_valid_chain(self, chain1):
        pprint(chain1.list_of_dicts())
        assert valid_chain(chain1) is True
        chain1._chain.append(chain1.last_block)
        pprint(chain1.list_of_dicts())
        assert chain1.is_valid() is False
        assert valid_chain(Blockchain()) is True

    def test_new_block(self, chain1):
        with pytest.raises(InvalidProofError):
            chain1.new_block(0)
        last_proof = chain1.last_block.proof
        chain1.new_block(proof_of_work(chain1.last_block.proof))
        assert valid_four_zeros_proof(last_proof, chain1.last_block.proof)

    def test_resolve_conflict(self, chain_lst, invalid_chain_lst):
        assert len(chain_lst[0]) == 1
        # Test short chain resolving conflicts
        res = chain_lst[0].resolve_chain_conflict(chain_lst[1:])
        assert res is True
        assert len(chain_lst[0]) == len(chain_lst)

        # Test longest chain resolving conflicts
        res2 = chain_lst[-1].resolve_chain_conflict(chain_lst[:-1])
        assert res2 is False
        assert len(chain_lst[-1]) == len(chain_lst)

        # Test resolve conflict with an invalid chain
        res3 = chain_lst[1].resolve_chain_conflict(invalid_chain_lst)
        assert res3 is False
        assert len(chain_lst[1]) == 2

    def test_from_list_of_dicts(self, chain1):
        print(chain1)
        chain_lst = chain1.list_of_dicts()
        pprint(chain_lst)
        new_chain = Blockchain.from_list_of_dicts(chain_lst)
        print(new_chain)
        assert new_chain == chain1

    def test_invalid_blockchain_index(self, chain1):
        chain_lst = chain1.list_of_dicts()
        chain_lst[-1]['index'] = 0
        pprint(chain_lst)
        assert not Blockchain.from_list_of_dicts(chain_lst).is_valid()


class TestNode:
    pass
