from block import hash_it, Block
import datetime
import secrets
import time

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.target = 0
        self.current_block = None

        # Create genesis block
        if len(self.chain) == 0:
            self.current_block = Block(index=0,
                              transactions=[],
                              previous_hash="Clouds in my coffee.",
                              target= self.get_target_value(block_index=0),
                              timestamp=time.time(),
                              nonce=0
            )
            #self.add_new_valid_block(new_block, 3680124643)
            self.target = self.get_target_value(block_index=0)

    def add_new_valid_block(self, nonce):

        curr_block = self.current_block
        # Get previous hash and add nonce in to compute new hash
        last_proof = curr_block.to_dict().get("previous_hash")
        curr_block.nonce = nonce
        curr_proof = curr_block.compute_hash()

        # If this is indeed a valid nonce then add it to the chain and auto
        # create a new current block to fix the timestamp for it
        is_valid = testNet.valid_proof(last_proof=last_proof, proof=curr_proof)
        if is_valid:
            self.chain.append(curr_block)
            self.current_block = self.get_current_block()
            self.target_value = self.get_target_value(len(self.chain))

    def get_target_value(self, block_index):
        # We can dynamically adjust the target value of zeroes here
        # but let's keep it at 4 for now
        return 4

    
    def get_previous_hash(self):

        prev_block = self.chain[-1]
        return prev_block.to_dict().get('hash')

    def get_current_block(self):

        num_blocks = len(self.chain)
        new_block = Block(index=num_blocks,
                          transactions=[],
                          previous_hash=self.get_previous_hash(),
                          target= "0"*self.get_target_value(block_index=num_blocks),
                          timestamp=None,
                          nonce=0
                    )

        return new_block
    
    def valid_proof(self, last_proof, proof):
        """
        Validates the proof: does hash(last_proof, proof) start with 4 leading zeros?
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hash_it(guess)


        return guess_hash, guess_hash[:self.target] == "0"*self.target