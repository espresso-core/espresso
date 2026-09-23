# ==========================================================
# IMPORTS
# ----------------------------------------------------------
import sys
import json
import secrets
import hashlib
import requests
import argparse

from datetime import datetime
from block import Block, hash_it

# ==========================================================
# FUNCTIONS
# ----------------------------------------------------------
def valid_proof(last_proof, proof, target):
    """
    Validates the proof: does hash(last_proof, proof) start with 4 leading zeros?
    """
    guess = f'{last_proof}{proof}'.encode()
    guess_hash = hash_it(guess)


    return guess_hash, guess_hash[:target] == "0"*target

import argparse

# Create the parser
parser = argparse.ArgumentParser(
    prog='miner',
    description='Example CLI that stores flags in variables'
)

# Add arguments
parser.add_argument('-a', '--algo', help='Mining algorithm')
parser.add_argument('-s', '--server', help='Pool address')
parser.add_argument('-n','--port', help='Pool port')
parser.add_argument('-u','--user', help='Pool loing/wallet address')
parser.add_argument('-p','--pass', help='Worker password (default x)')

# Parse arguments
args = parser.parse_args(sys.argv[1:])


NODE_URL = f"{args.server}:{args.port}"  # change to your Flask node URL
MINER_ADDRESS = "jesse-miner-001"   # any identifier for rewards


print(f"ABOUT:     SeaMiner")
print(f"POOL:      {NODE_URL}")
print(f"ALGORITHM: {args.algo}")



def get_block_template():
    """
    GET /getblocktemplate -> { "index": ..., "proof": ..., "previous_hash": ... }
    """
    resp = requests.get(f"{NODE_URL}/getblocktemplate")
    resp.raise_for_status()
    return resp.json()

def get_balance(address):
    """
    GET /balance/{adddress} -> { "address": ..., "balance": ...}
    """
    resp = requests.get(f"{NODE_URL}/balance/{address}")
    resp.raise_for_status()
    return resp.json()

def report_message(message):

    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    status = message.get("status")
    reward = message.get("reward")

    print(f"[{timestamp}] - Block Found - {status} - Reward ({reward})")

def mine_block():

    # Mine continously
    while True:

        # get block info from server and convert to Block object
        block_json = get_block_template()
        curr_block = Block(index=block_json.get("index"), 
                            transactions=block_json.get("transactions"), 
                            previous_hash=block_json.get("previous_hash"), 
                            target=block_json.get("target"), 
                            timestamp=block_json.get("timestamp"), 
                            nonce=block_json.get("nonce")
                            )

        # run the miner continuously
        while True:

            # select a nonce to hash with
            nonce = secrets.randbelow(pow(2, 32))

            # get information for the has to check if the proof is valid
            last_proof = curr_block.to_dict().get("previous_hash")
            curr_block.nonce = nonce
            curr_proof = curr_block.compute_hash()
            target = curr_block.target

            # check if hash proof is valid according to block target (assigned by blockchain)
            hash, is_valid = valid_proof(last_proof=last_proof, proof=curr_proof, target=target)

            if is_valid:

                # send block back to server for a second check and add if still valid
                payload = {"jsonrpc": "2.0",
                        "method": "submitblock",
                        "id": 1,
                        "nonce": nonce}
                resp = requests.post(f"{NODE_URL}/submitblock", json=json.dumps(payload))
                resp.raise_for_status()
                message = resp.json()

                report_message(message)
                break

if __name__ == "__main__":
    mine_block()