import hashlib
import time
import json

def hash_it(data: bytes) -> str:
        SCRYPT_N, SCRYPT_R, SCRYPT_P = 1024, 1, 1  # Litecoin/Dogecoin's real, proven parameters
        return hashlib.scrypt(data, salt=data, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P, dklen=32).hex()


class Block:
    
    """
    compute_merkle_root
    header_string
    compute_hash
    header_string
    to_dict
    from_dict
    """

    def __init__(self, index, transactions, previous_hash, target, timestamp=None, nonce=0):
        self.index = index
        self.transactions = transactions  # list[Transaction]
        self.previous_hash = previous_hash
        self.target = target
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.nonce = nonce
        self.merkle_root = self.compute_merkle_root()

    def compute_merkle_root(self):
        # The Merkle Root of an empty list of items will be all zeroes.
        if not self.transactions:
            return "0" * 64

        # Has every item in the list, for the first time
        level = [hash_it(str(item).encode()) for item in self.transactions]
        #level = [tx.hash() for tx in self.transactions]

        # Iterate over the list and continue hashing in pairs until only one remains
        while len(level) > 1:
            next_level = []

            # If odd number of nodes, duplicate the last one
            if len(level) % 2 == 1:
                level.append(level[-1])

            # Hash pairs together (hash_it takes bytes and returns a string)
            for i in range(0, len(level), 2):
                left = level[i].encode()
                right = level[i + 1].encode()

                print([left, right])
                next_level.append(hash_it(left + right))

            level = next_level

        return level[0]

    def header_string(self):

        header = {
            "index": self.index,
            "timestamp": self.timestamp,
            "merkle_root": self.merkle_root,
            "previous_hash": self.previous_hash,
            "target": self.target,
            "nonce": self.nonce,
        }
        return json.dumps(header, sort_keys=True)

    def compute_hash(self):
        s = self.header_string().encode()
        return hash_it(s)

    def to_dict(self):

        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "target": self.target,
            "nonce": self.nonce,
            "merkle_root": self.merkle_root,
            "hash": self.compute_hash(),
        }

    def from_dict(d):
        return Block(
            d["index"],
            d["transactions"],
            d["previous_hash"],
            d["target"],
            d["timestamp"],
            d["nonce"]
        )