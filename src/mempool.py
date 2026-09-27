import json
from wallet import verify_transaction


class Mempool():
    def __init__(self):
        self.transactions = []

    def merge_mempool(self, mempool_data):

        # Let's verify all of the signed transactions first and keep only the valid ones
        valid_external_txs = []
        for signed_tx in mempool_data:
            if verify_transaction(signed_tx):
                valid_external_txs.append(signed_tx)

        # serialize our and our peers mempool transactions
        serialized_internal = [json.dumps(tx) for tx in self.transactions]
        serialized_external = [json.dumps(tx) for tx in valid_external_txs]

        # Throw all mempool data into one giant copy and keep what's unique
        serialized_internal.extend(serialized_external)
        serialized_internal = list(set(serialized_internal))

        # deserialize all of the transaction (they're all unique now)
        self.transactions = [json.loads(tx) for tx in serialized_internal]