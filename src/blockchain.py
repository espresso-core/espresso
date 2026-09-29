from block import hash_it, Block
import datetime
import secrets
import time
import json

class Blockchain:
    def __init__(self):
        self.chain = []
        self.target = 0
        self.current_block = None
        self.mempool = []
        self.balances = {}
        self.block_file = "blocks.dat"
        self.genesis_hash = "Clouds in my coffee."

        # Create genesis block
        if len(self.chain) == 0:

            # Create and insert the template for the COIN_BASE transaction
            cb_tx = self.create_coinbase_transaction()
            txs = self.mempool
            txs.insert(0, cb_tx)

            self.current_block = Block(index=0,
                              transactions=txs,
                              previous_hash=self.genesis_hash,
                              target= self.get_target_value(block_index=0),
                              timestamp=time.time(),
                              nonce=0
            )
            self.target = self.get_target_value(block_index=0)


    def add_new_valid_block(self, new_block_dict: dict):

        new_block = Block.from_dict(new_block_dict)

        # Update balances to reflect new coin spend
        txs = new_block_dict.get('transactions')
        for tx in txs:
            SENDER = tx.get('transaction').get("sender")
            RECIPIENT = tx.get('transaction').get("recipient")
            AMOUNT = tx.get('transaction').get("amount")

            if RECIPIENT in self.balances.keys():
                self.balances[RECIPIENT] += AMOUNT
            else:
                self.balances[RECIPIENT] = AMOUNT

            if SENDER != "COIN_BASE":
                self.balances[SENDER] -= AMOUNT


        self.chain.append(new_block)                           # add it to chain, its valid
        self.save_block_to_disk(new_block_dict)                # save it to disk, for backup
        self.current_block = self.get_current_block()          # get new current block
        self.target = self.get_target_value(len(self.chain))   # set the new target difficult
            
        return True


    def get_target_value(self, block_index):
        # We can dynamically adjust the target value of zeroes here
        # but let's keep it at 4 for now
        return 3


    def get_reward_value(self, block_index):
        # We can dynamically adjust the reward value here but let's
        # keep it at 25 for now.
        return 25

    
    def get_previous_hash(self):

        if self.chain == []:
            return self.genesis_hash
        else:
            prev_block = self.chain[-1]
            return prev_block.to_dict().get('hash')

    def get_current_block(self):

        num_blocks = self.get_chain_height()

        # Create and insert the template for the COIN_BASE transaction
        cb_tx = self.create_coinbase_transaction()
        txs = self.mempool
        txs.insert(0, cb_tx)

        new_block = Block(index=num_blocks,
                          transactions=txs,
                          previous_hash=self.get_previous_hash(),
                          target=self.get_target_value(block_index=num_blocks),
                          timestamp=None,
                          nonce=0
                    )

        # Clear the internal mempool since they were consumed
        self.mempool = []

        return new_block
    
    def valid_proof(self, last_proof, proof):
        """
        Validates the proof: does hash(last_proof, proof) start with correct leading zeros?
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hash_it(guess)


        return guess_hash[:self.target] == "0"*self.target


    def get_chain_height(self):
        """
        Return the number of blocks in the current chain
        """

        return len(self.chain)


    def get_block(self, block_num):
        """
        Returns the dict representation of a block.
        Checks memory first then resorts to disk
        """
        # Go through all blocks on the in-mem chain
        for block_dict in self.chain:
            if block_dict.get("index") == block_num:
                return block_dict

        return self.get_block_from_disk(block_num)



    def get_block_from_disk(self, block_num):
        try:
            with open(self.block_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:  # Skip empty lines
                        continue
                    try:
                        item = json.loads(line)
                        #print(item)  # Process the JSON object

                        if item.get("index") == block_num:
                            return item
                    except json.JSONDecodeError as e:
                        print(f"Skipping invalid JSON line: {e}")

            # block definitely not on disk
            return {}
        
        except FileNotFoundError:
            print(f"File not found: {self.block_file}")


    def get_block_field(self, block_num, field_name):
        block = self.get_block(block_num)
        return block.get(field_name)


    def get_chain_info(self):

        return {"chainheight": self.get_chain_height(),
                "target": self.target,
                "previoushash": self.get_previous_hash(),
                "reward": self.get_reward_value()
                }


    def mempool_empty(self):
        if len(self.mempool) == 0:
            return True
        else:
            return False

    def save_block_to_disk(self, json_data: dict):

        # Append each JSON object on a new line
        with open(self.block_file, "a") as f:
            json.dump(json_data, f)  # Write JSON object
            f.write("\n")       # Add newline after each object

    def get_current_reward(self):

        CHAIN_HEIGHT = len(self.chain)
        return self.get_reward_value(CHAIN_HEIGHT)

    def create_coinbase_transaction(self):

        # No one signs the coinbase transaction because 
        return {'transaction': {'sender': 'COIN_BASE', 'recipient': 'MINER', 'amount': self.get_current_reward()},
                'signature': '',
                'public_key': ''
                }

    def get_balance(self, wallet_address):
        return self.balances.get(wallet_address,0)