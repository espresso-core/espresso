import os
import json
import time

class Peerpool():
    def __init__(self, PEERS_FILE):
        self.peers_file = PEERS_FILE
        self.valid_peers = {}
        self.pending_peers = {}
        self.banned_peers = {}

        self.load_peers_file()


        #{ADDRESS: {'last_contact': time.time(), 'public_key': "AAAA"}
            
    def save_peers_file(self):
        """
        Flush the valid peer records list to disk
        """

        print(self.valid_peers)
        with open(self.peers_file, "w+") as f:
            for peer, peer_data in self.valid_peers.items():

                data = {peer: peer_data}
                f.write(json.dumps(data) + "\n") # Add a newline character after each line


    def load_peers_file(self):
        """
        Try to load the peer records list from disk
        """
        if os.path.isfile(self.peers_file):
            with open(self.peers_file, "r") as f:
                for line in f:
                    print(json.loads(line))
                    self.valid_peers.update()
        else:
            print("File does not exist or is not a file.")


    def add_banned_peer(self, data: dict):
        """
        Copy peer record to banned list then remove from valid list
        """
        self.banned_peers.update(data)
        self.remove_valid_peer(data)


    def remove_valid_peer(self, data:dict):
        """
        Remove peer record from valid peers record list
        """
        address, peer_data = data
        del(self.valid_peers[address])


    def add_pending_peer(self, data: dict):
        """
        Move peer record 
        """
        if len(data)==1:
            
            # This peer should not already exist in pending or valid peers list, otherwise add it
            for address, peer_data in data.items():

                if (address not in self.valid_peers.keys()) & \
                (address not in self.banned_peers.keys()) & \
                (address not in self.pending_peers.keys()):

                    self.pending_peers.update(data)

    def move_pending_to_valid(self, address):
        """
        Move peer record from pending list to valid list
        """
        # Copy this data to valid peers list
        peer_data = self.pending_peers.get(address)
        self.valid_peers[address] = peer_data

        # Rempve this address from pending peers list
        self.remove_pending_peer(address)


    def remove_pending_peer(self, address):
        """
        Delete peer record from pending list
        """
        del(self.pending_peers[address])


    def remove_valid_peer(self, address):
        """
        Delete peer record from valid list
        """
        del(self.valid_peers[address])


    def update_peer_field(self, address, field_name, value):
        """
        Update a field value in peer data record
        """
        peer_data = self.valid_peers[address]
        peer_data[field_name] = value
        self.valid_peers[address] = peer_data