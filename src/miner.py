# ==========================================================
# IMPORTS
# ----------------------------------------------------------
import sys
import json
import time
import secrets
import hashlib
import requests
import argparse

from rpc import rpc_post
from datetime import datetime
from block import Block, hash_it

# ==========================================================
# FUNCTIONS
# ----------------------------------------------------------


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

JSON_RPC_URL = f"{NODE_URL}/jsonrpc"

def get_block_template():
    """
    GET /getblocktemplate -> { "index": ..., "proof": ..., "previous_hash": ... }
    """

    result = rpc_post(JSON_RPC_URL, "sso_getblocktemplate", [])
    return result



def report_message(message):

    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    status = message.get("status")
    reward = message.get("reward")

    print(f"[{timestamp}] - Block Found - {status} - Reward ({reward})")

def report_hashrate(elapsed_time, hash_count):

    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    hash_rate = hash_count / elapsed_time

    print(f"[{timestamp}] - Hash Rate - {round(hash_rate,2)} H/s.")


def mine_block():

    time_start = time.time()
    last_report = time_start
    hash_count = 0

    # Mine continously
    while True:
        try:
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

                hash_count += 1

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

                    data = rpc_post(JSON_RPC_URL, "sso_submitblock", [nonce])
                    report_message(data)

                    #data = rpc_post(JSON_RPC_URL, "sso_getchainheight", [])
                    #print(f'Chain Height: {data}')

                    break

                timestamp = time.time()

                if timestamp - last_report > 10:
                    elapsed_time = timestamp - time_start
                    last_report = timestamp

                    report_hashrate(elapsed_time, hash_count)

        except Exception as e:

            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

            print(f"[{timestamp}] - Unable to connect. Retrying in 5 seconds.")

            time.sleep(5)

        
if __name__ == "__main__":
    mine_block()