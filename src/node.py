from block import Block
from blockchain import Blockchain
import json


from flask import Flask, jsonify, request

testNet = Blockchain()

app = Flask(__name__)
 
balances = {
    "fb82a34bdd491703f4935cd963505af2dd9d0f8f": 12.5,
    "def456": 100.0
}

@app.route("/getblocktemplate", methods=['GET'])
def get_new_block():
    """
    Return the current unsolved block of the BlockChain in json format
    """
    return testNet.current_block.to_dict(), 200

@app.route("/submit_block", methods=['POST'])
def submit_block():
    """
    Received block solution.
    """

    # Get data from post
    values_str = request.get_json()
    values = json.loads(values_str)
    nonce = values.get('nonce')

    # verify the block solution, then add to network if needed
    res = testNet.add_new_valid_block(nonce)

    # respond to the caller with some data
    if res:
        response = {'status': 'Accepted',
                    'reward': '25'}
        return jsonify(response), 201
    else:
        response = {'status': 'Rejected',
                    'reward': '0'}
        return jsonify(response), 201


@app.route("/balance/<address>", methods=['GET'])
def get_balance(address):
    """
    Return the balance of a wallet address.
    """

    
    balance = balances.get(address, 0)
 
    return jsonify({
        "address": address,
        "balance": balance
    })

if __name__ == "__main__":
    app.run()