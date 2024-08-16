import os
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

DELAYS = {
    'ACCOUNT': [5, 15],  # delay between connections to accounts (the more accounts, the longer the delay)
    'REPEAT': [300, 600],
    'BUY_CARD': [2, 5],  # delay before buy a upgrade cards
}

# need buy a cards
BUY_CARD = True

# need buy upgrades
BUY_UPGRADE = True

# session folder (do not change)
WORKDIR = "sessions/"

# timeout in seconds for checking accounts on valid
TIMEOUT = 30
