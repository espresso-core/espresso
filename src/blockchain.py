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
            #self.add_new_valid_block(new_block, 3680124643)
            self.target = self.get_target_value(block_index=0)

    def verify_block(self, minerBlock: dict):

        try:
            chainBlock = self.current_block.to_dict()

            # Check previous hash
            elemA = chainBlock.get("previous_hash")
            elemB = minerBlock.get("previous_hash")

            if elemA != elemB:
                return False

            # check the indices
            elemA = chainBlock.get("index")
            elemB = minerBlock.get("index")

            if elemA != elemB:
                return False

            # verify the transactions match
            elemA = [json.dumps(tx, sort_keys=True) for tx in chainBlock.get("transactions")[1:]]   # skip the coinbase
            elemB = [json.dumps(tx, sort_keys=True) for tx in minerBlock.get("transactions")[1:]]

            if elemA != elemB:
                return False

            
            # verify coinbase reward is accurate
            elemA = chainBlock.get("transactions")[0].get("reward")
            elemB = chainBlock.get("transactions")[0].get("reward")

            if elemA != elemB:
                return False
            
            return True
        
        except Exception as e:
            print(e)



    def add_new_valid_block(self, new_block):

        
    
        curr_block = self.current_block
        
        # Get previous hash and add nonce in to compute new hash
        last_proof = new_block.get("previous_hash")
        curr_proof = Block.from_dict(new_block).compute_hash()
        

    
        # If this is indeed a valid nonce then add it to the chain and auto
        # create a new current block to fix the timestamp for it
        is_valid = self.valid_proof(last_proof=last_proof, proof=curr_proof)

        if is_valid:
            self.chain.append(curr_block)                           # add it to chain, its valid
            self.save_block_to_disk(curr_block)                     # save it to disk, for backup
            self.current_block = self.get_current_block()           # get new current block
            self.target = self.get_target_value(len(self.chain))    # set the new target difficult
            return True
        else:
            return False

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

        num_blocks = len(self.chain)

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


    def get_chain_block(self, block_num):
        return self.chain[block_num]


    def get_chain_info(self):

        return {"chainheight": len(self.chain),
                "target": self.target,
                "previoushash": self.get_previous_hash(),
                "reward": self.get_reward_value()
                }


    def mempool_empty(self):
        if len(self.mempool) == 0:
            return True
        else:
            return False

    def save_block_to_disk(self, block):

        # Append each JSON object on a new line
        with open(self.block_file, "a") as f:
            json.dump(block.to_dict(), f)  # Write JSON object
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