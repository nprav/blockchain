# Script used to generate arbitrary transactions and Blockchains
# The data will be randomized with a given seed. It will be used to help with
# testing the implementation.

# Standard library imports
import random
from string import ascii_letters


# Initialize Random Number generator
random.seed(42)


# Function to generate random transactions
def gen_random_transaction_dict():
    sender = random.choice(ascii_letters)
    recipient = random.choice(ascii_letters.replace(sender, ''))
    return {
        'sender': sender,
        'recipient': recipient,
        'amount': random.uniform(0, 100),
    }

# Function to generate random commands
