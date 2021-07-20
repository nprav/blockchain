# June 25th 2021
# Basic Blockchain implementation
# Praveer Nidamaluri
# Based on tutorial available in:
#   https://hackernoon.com/learn-blockchains-by-building-one-117428612f46

# Standard library imports

# Third party imports

# Local application imports
from blockchain.__init__ import create_blockchain_application

raw_port = input("Choose Port number (default = 5000): ")
try:
    port = int(raw_port)
except ValueError:
    print("Invalid input. Default port = 5000 used.")
    port = 5000
finally:
    if port <= 0:
        port = 5000


# Main Flask Function
app = create_blockchain_application()
app.run(
    port=port,
)
