import json
import time


class Peerpool():
    def __init__(self):
        self.valid_peers = {}
        self.pending_peers = {}

        #{ADDRESS: {'last_contact': time.time(), 'public_key': "AAAA"}
            
    def add_pending_peer(self, data: dict):

        if len(data)==1:
            
            # This peer should not already exist in pending or valid peers list, otherwise add it
            for address, peer_data in data.items():

                if (address not in self.valid_peers.keys()) & \
                (address not in self.pending_peers.keys()):

                    self.pending_peers.update(data)

    def move_pending_to_valid(self, address):

        # Copy this data to valid peers list
        peer_data = self.pending_peers.get(address)
        self.valid_peers[address] = peer_data

        # Rempve this address from pending peers list
        self.remove_pending_peer(address)

    def remove_pending_peer(self, address):
        del(self.pending_peers[address])

    def remove_valid_peer(self, address):
        del(self.valid_peers[address])