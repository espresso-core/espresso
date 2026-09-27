from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError
import hashlib
import binascii
import json

class Wallet():

    def __init(self):
        self.private_key = None
        self.private_key_hex = None
        self.private_key_bytes = None

        self.public_key = None
        self.public_key_hex = None
        self.public_key_bytes = None

        self.wallet_address = ""

    def generate_wallet(self):
        try:
            # Generate private key
            self.private_key = SigningKey.generate(curve=SECP256k1)
            self.private_key_bytes = self.private_key.to_string()
            self.private_key_hex = self.private_key_bytes.hex()

            # Generate public keys
            self.public_key = self.private_key.get_verifying_key()
            self.public_key_bytes = self.public_key.to_string()
            self.public_key_hex = self.public_key_bytes.hex()

            # Simple wallet address
            sha256_hash = hashlib.sha256(bytes.fromhex(self.public_key_hex)).digest()
            ripemd160 = hashlib.new("ripemd160",sha256_hash).digest()
            self.wallet_address = binascii.hexlify(ripemd160).decode()

        except Exception as e:
            print(e)

    def import_keys(self, private_key_hex, public_key_hex):

        # Load Public key from hex
        self.public_key_hex = public_key_hex.rstrip()
        self.public_key_bytes = binascii.unhexlify(self.public_key_hex.strip())
        self.public_key = VerifyingKey.from_string(self.public_key_bytes, curve=SECP256k1)

        # Load Private key from hex
        self.private_key_hex = private_key_hex.rstrip()
        self.private_key_bytes = binascii.unhexlify(self.private_key_hex.strip())
        self.private_key = SigningKey.from_string(self.private_key_bytes, curve=SECP256k1)


    def sign_transaction(self, sender: str, recipient: str, amount: float) -> dict:
        """
        Create and sign a transaction.
        Returns a dict with transaction data and signature.
        """
        if not sender or not recipient:
            raise ValueError("Sender and recipient addresses must be provided.")
        if amount <= 0:
            raise ValueError("Amount must be positive.")

        # Create transaction payload
        transaction = {
            "sender": sender,
            "recipient": recipient,
            "amount": amount
        }

        # Serialize and hash transaction
        tx_json = json.dumps(transaction, sort_keys=True).encode()
        tx_hash = hashlib.sha256(tx_json).digest()

        # Sign the hash
        signature = self.private_key.sign(tx_hash)

        return {
            "transaction": transaction,
            "signature": binascii.hexlify(signature).decode(),
            "public_key": self.public_key_hex
        }


def verify_transaction(transaction_data: dict) -> bool:
    """
    Verify a signed transaction.
    transaction_data must contain:
    - transaction (dict)
    - signature (hex)
    - public_key (hex)
    """
    try:
        tx_json = json.dumps(transaction_data["transaction"], sort_keys=True).encode()
        tx_hash = hashlib.sha256(tx_json).digest()

        public_key_bytes = binascii.unhexlify(transaction_data["public_key"])
        verifying_key = VerifyingKey.from_string(public_key_bytes, curve=SECP256k1)

        signature_bytes = binascii.unhexlify(transaction_data["signature"])
        verifying_key.verify(signature_bytes, tx_hash)
        return True
    except (KeyError, binascii.Error, BadSignatureError, ValueError):
        return False