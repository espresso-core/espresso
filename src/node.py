import json
from flask import Flask, request, jsonify
from typing import Any, Dict, List
from block import Block
from blockchain import Blockchain
import json
import threading
import time
import requests

from rpc import rpc_post


# =================================================
# Node configuration
# -------------------------------------------------
MONITOR_PEERS_INTERVAL = 60
MAX_ELAPSED_PEER_CONTACT_TIME = MONITOR_PEERS_INTERVAL*10

MONITOR_MEMPOOL_INTERVAL = 60


# =================================================
# Start / Setup Background Threads
# -------------------------------------------------
def monitor_mempool():

    global mempool
    
    while True:
        # Sync with the mempools of our peers
        # ------------------------------------------------------
        for peer_id, peer_data in allocated_peers.items():

            # unpack peer data dict into variables (order matters)
            host, port, last_contact = peer_data.values()

            try:
                # Ping the other node
                JSON_RPC_URL = f"http://{host}:{port}/jsonrpc"
                data = rpc_post(JSON_RPC_URL, "sso_mempool", [])

                # serialize our and our peers mempool transactions
                serialized_set_ours = [json.dumps(tx) for tx in data]
                serialized_set_peer = [json.dumps(tx) for tx in mempool]

                # Throw all mempool data into one giant copy and keep what's unique
                new_mempool = serialized_set_ours.copy()
                new_mempool.extend(serialized_set_peer)
                new_mempool = list(set(new_mempool))

                # deserialize all of the transaction (they're all unique now)
                new_mempool = [json.loads(tx) for tx in new_mempool]

                # Reassign our local copy of the mempool with this one
                mempool = new_mempool

                print(f"[Thread - Mempool] [{peer_id}@{host}:{port}] - Synced.")

            except Exception as e:
                print(e)
                print(f"[Thread - Mempool] [{peer_id}@{host}:{port}] - Error.")

        
        time.sleep(MONITOR_MEMPOOL_INTERVAL)  # Check every 5 seconds

# Background thread function
def monitor_network():

    # define global variables this thread has access to
    global allocated_peers

    while True:

        clean_allocated_peers_list = {}

        # Check on the aliveness of exisiting peers
        # ------------------------------------------------------
        for peer_id, peer_data in allocated_peers.items():

            # unpack peer data dict into variables (order matters)
            host, port, last_contact = peer_data.values()

            now = time.time()
            elapsed_time = 0

            try:
                # Ping the other node
                JSON_RPC_URL = f"http://{host}:{port}/jsonrpc"
                data = rpc_post(JSON_RPC_URL, "sso_ping", [])

                # Check how long it's been since we last heard from peer
                elapsed_time = now - last_contact

                # Reset the last contact time with now
                allocated_peers[peer_id]['last_contact'] = now

                print(f"[Thread - Network] [{peer_id}@{host}:{port}] - Alive - ({elapsed_time})")
                
            except:
                now = time.time()
                elapsed_time = now - last_contact
                print(f"[Thread - Network] [{peer_id}@{host}:{port}] - No Response - ({elapsed_time})")


            # If we haven't heard from you in so long, drop you from peers list
            if elapsed_time >= MAX_ELAPSED_PEER_CONTACT_TIME:
                print(f"[Thread - Network] [{peer_id}@{host}:{port}] - Dropped - ({elapsed_time})")
            else:
                # Retain a copy into the new list
                clean_allocated_peers_list[peer_id] = allocated_peers[peer_id]

        allocated_peers = clean_allocated_peers_list.copy()

        time.sleep(MONITOR_PEERS_INTERVAL)  # Check every 5 seconds


# =================================================
# Start / Setup Blockchain
# -------------------------------------------------
Chain = Blockchain()

balances = {
    "AAAA": 12.5,
    "BBBB": 100.0,
    "CCCC": 1
}

candidate_peers = {}
allocated_peers = {
                    "AAAAA": {'host': "127.0.0.1", 'port': 4444, 'last_contact': time.time()}
                    }

mempool = []

# Add a single transaction for testing purposes
tx = {"sender": "AAAA", "recipient": "BBBB", "amount": 100, "timestamp": time.time()}
mempool.append(tx)



# =================================================
# Start / Setup Flask Server
# -------------------------------------------------

app = Flask(__name__)

# Example blockchain methods
def sso_getdifficulty():
    return Chain.target

def sso_getblockheight():
    return len(Chain.chain)

def sso_getpeercount():
    return len(allocated_peers)

def sso_mempool():
    return mempool

def sso_mempoolsize():
    return len(mempool)

def sso_ping():
    return "alive"

def sso_getchainheight():
    return Chain.get_chain_height()

def sso_getpeers():
    return allocated_peers

def sso_getbalance(address):
    """
    Return the balance of a wallet address.
    """
    balance = balances.get(address, 0)
 
    return {
        "address": address,
        "balance": balance
    }

def sso_getblocktemplate():
    """
    Return the current unsolved block of the BlockChain in json format
    """
    return Chain.current_block.to_dict()


def sso_submitblock(nonce):
    """
    Submit a block to the blockchain as a candidate solution
    """
   # verify the block solution, then add to network if needed
    res = Chain.add_new_valid_block(nonce)

    # respond to the caller with some data
    if res:
        response = {'status': 'Accepted',
                    'reward': '25'}
        return response
    else:
        response = {'status': 'Rejected',
                    'reward': '0'}
        return response

# Register methods
app.jsonrpc_methods = {
    "sso_getbalance": sso_getbalance,
    "sso_getblocktemplate": sso_getblocktemplate,
    "sso_submitblock": sso_submitblock,
    "sso_getchainheight": sso_getchainheight,
    "sso_getpeers": sso_getpeers,
    "sso_ping": sso_ping,
    "sso_mempool": sso_mempool,
    "sso_mempoolsize": sso_mempoolsize,
    "sso_getpeercount": sso_getpeercount,
    "sso_getblockheight": sso_getblockheight,
    "sso_getdifficulty": sso_getdifficulty
}




# =================================================
# Start / Setup JSONRPC endpoint
# -------------------------------------------------
@app.route("/jsonrpc", methods=["POST"])
def jsonrpc():
    raw = request.data
    try:
        req = json.loads(raw)

    except json.JSONDecodeError:
        return jsonify({
            "jsonrpc": "2.0",
            "error": {"code": -32700, "message": "Parse error"},
            "id": None
        }), 400

    # Validate JSON-RPC 2.0 envelope
    if not isinstance(req, dict) or req.get("jsonrpc") != "2.0":
        return jsonify({
            "jsonrpc": "2.0",
            "error": {"code": -32600, "message": "Invalid Request"},
            "id": req.get("id")
        }), 400



    method = req.get("method")
    params = req.get("params", [])
    id_val = req.get("id")

    if method not in app.jsonrpc_methods:
        return jsonify({
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": "Method not found"},
            "id": id_val
        }), 400

    try:
        result = app.jsonrpc_methods[method](*params)
    except Exception as e:
        return jsonify({
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": str(e)},
            "id": id_val
        }), 500


    return jsonify({
        "jsonrpc": "2.0",
        "result": result,
        "id": id_val
    }), 200

if __name__ == "__main__":

    threading.Thread(target=monitor_network, daemon=True).start()
    threading.Thread(target=monitor_mempool, daemon=True).start()
    app.run(host="127.0.0.1", port=3333)