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

    def add_transaction(self, tx):
        """
        Add a single transaction to the pool
        """

        if self.exists(tx):
            return False
        else:
            self.transactions.append(tx)
            return True

    def add_transactions(self, tx_list):
        """
        Add a sequential list of transactions to the pool
        """

        for tx in tx_list:
            self.add_transaction(tx)

    def exists(self, tx):
        """
        Check if a transaction already exists
        """
        
        hash_tx = json.dumps(tx)
        hash_txs = [json.dumps(tx) for tx in self.transactions]

        if hash_tx in hash_txs:
            return True
        else:
            return False

    def select_transactions(self, n):

        # Just grab the first n, however they're ordered and optmized this later
        actual_n = min(len(self.transactions), n)

        selected_txs = self.transactions[:actual_n]
        self.transactions = self.transactions[actual_n:]

        return selected_txs