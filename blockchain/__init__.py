# June 25th 2021
# Basic Blockchain implementation
# Praveer Nidamaluri
# Based on tutorial available in:
#   https://hackernoon.com/learn-blockchains-by-building-one-117428612f46

# Standard library imports
from uuid import uuid4
import json

# Third party imports
from flask import Flask, jsonify, request, Response

# Local application imports
from blockchain.internals import BlockchainNode, Blockchain, Transaction, \
    proof_of_work, valid_chain


def create_blockchain_application() -> Flask:
    """Function that contains the networking setup for the
    Blockchain. Handles the Blockchain and Blockchain network."""

    # Flask app instantation
    app = Flask(__name__)
    blockchain = Blockchain()

    # Globally unique address for node
    node_id = str(uuid4()).replace('-', '')
    network = BlockchainNode(node_id, blockchain)

    @app.route('/', methods=['GET'])
    def main_page() -> str:
        """Display a basic intro. page."""
        return "Basic Blockchain Implementation."

    @app.route('/mine', methods=['GET'])
    def mine() -> [Response, int]:
        """Mine a new block. Perform proof of work to get the new proof. Add
        reward for the mining. mine the new block.

        Returns
        -------
        Response    Json response with a message, the new block, the new index,
                    the transactions in the new block, and the reward to the
                    miner.
        int         HTTP response code.
        """
        proof = proof_of_work(blockchain.last_block.proof)

        # Add reward for current miner to the transactions
        blockchain.new_transaction(
            sender='0',
            recipient=node_id,
            amount=1,
        )

        # Mine new block
        new_block = blockchain.new_block(proof)
        response = {
            'message': f'Block {new_block.index} mined.',
            'index': new_block.index,
            'transactions': new_block.dict()['transactions'],
            'reward': 1,
        }
        return jsonify(response), 200

    @app.route('/transactions/new', methods=['POST'])
    def new_transaction() -> [Response, int]:
        """Get a new transaction. Verify if all the required details are
        uploaded. If so, add the transaction to the chain.

        Returns
        -------
        Response    Message that either the Transaction has been added, or not.
        int         HTTP response code
        """
        keys = request.form.keys()
        if set(keys) != {'sender', 'recipient', 'amount'}:
            response = {
                'message': f"Invalid data.",
            }
            code = 400
        else:
            # TODO: Handle exceptions raised by Blockchain
            index = blockchain.new_transaction(**request.form)
            response = {
                'message': f'Transaction will be added to block {index}',
            }
            code = 201
        return jsonify(response), code

    @app.route('/chain', methods=['GET'])
    def full_chain() -> [Response, int]:
        """Return the full Blockchain.

        Returns
        -------
        Response    Response with blockchain as a list of dicts and the chain
                    length.
        int         HTTP response code
        """
        response = {
            'chain': blockchain.list_of_dicts(),
            'length': len(blockchain),
        }
        return jsonify(response), 200

    @app.route('/nodes/register', methods=['POST'])
    def new_nodes() -> [Response, int]:
        try:
            raw_data = request.get_json()
            nodes = raw_data.get('nodes')
        except KeyError:
            return "Error: No new nodes have been provided."

        if nodes is None:
            return "Error: No new nodes have been provided."

        num_nodes = len(network.nodes)
        for node in nodes:
            if node is not "":
                network.register_node(node)

        response = {
            'message': 'New nodes have been added.',
            'total_nodes': list(network.nodes),
        }
        if len(network.nodes) == num_nodes:
            response['message'] = 'No new nodes have been added.'

        return jsonify(response), 200

    @app.route('/nodes/resolve', methods=['GET'])
    def consensus() -> [Response, int]:
        replaced = network.resolve_conflicts()

        if replaced:
            response = {
                'message': 'Chain was replaced.',
                'new_chain': blockchain.list_of_dicts(),
            }

        else:
            response = {
                'message': 'Chain is authoritative.',
                'chain': blockchain.list_of_dicts(),
            }
        return jsonify(response), 200

    return app


if __name__ == '__main__':

    # Test Functions
    test_transaction = Transaction("sender", recipient="rec", amount=3)
    test_transaction2 = Transaction("sender", recipient="rec", amount='3')
    print(test_transaction)
    print(test_transaction)
    print(type(test_transaction))

    test_chain = Blockchain()
    test_chain.new_transaction('test', 'test', 3)
    print(test_chain.unconfirmed_transactions)
    print(valid_chain(test_chain))
    test_chain.new_block(proof_of_work(test_chain.last_block.proof))
    print(valid_chain(test_chain))
    test_chain._chain.append(test_chain.last_block)
    print(valid_chain(test_chain))
    print(test_chain.unconfirmed_transactions)
    print(test_chain.list_of_dicts())
    print(test_chain.last_block)
    print(test_chain.last_block.hash())
    print(proof_of_work(test_chain.last_block.proof))

    # Main Flask Functions
    app = create_blockchain_application()
    app.run(
        port=5000,
    )

