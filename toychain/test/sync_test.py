import logging
import sys

sys.path.append("/home/eksander/toychain-argos/")

from toychain.src.Node import Node
from toychain.src.consensus.ProofOfAuth import ProofOfAuthority
from toychain.src.Block import Block, State
from toychain.src.Transaction import Transaction
from toychain.src.constants import LOCALHOST
from toychain.src.utils import gen_enode


auth_signers = [gen_enode(i) for i in range(1,4)]
initial_state = State()

GENESIS_BLOCK = Block(0, 0000, [], auth_signers, 0, 0, 0, nonce = 1, state = initial_state)
CONSENSUS = ProofOfAuthority(genesis = GENESIS_BLOCK)

# Create the nodes with (id, host, port, consensus_protocol)
node1 = Node(1, LOCALHOST, 1234, CONSENSUS)
node2 = Node(2, LOCALHOST, 1235, CONSENSUS)
node3 = Node(3, LOCALHOST, 1236, CONSENSUS)

logging.basicConfig(level=logging.INFO)

def init_network():
    
    # Start the TCP for syncing mempool and blockchain
    node1.start_tcp()
    node2.start_tcp()
    node3.start_tcp()
    
    # Start the mining process for each node
    node1.start_mining()
    node2.start_mining()
    node3.start_mining()

    # Add the peers of each node
    node1.add_peer(node2.enode)
    node1.add_peer(node3.enode)
    node2.add_peer(node1.enode)
    node2.add_peer(node3.enode)
    node3.add_peer(node1.enode)
    node3.add_peer(node2.enode)

import time
if __name__ == '__main__':

    init_network()

    # Setup simulation steps
    max_steps = 15000
    curr_step = 0
    step = 1

    while True:
        print(curr_step)
        node1.step()
        node2.step()
        node3.step()
        # time.sleep(0.05)
        curr_step += step
        if curr_step>max_steps:
            break
    
    # Display the final blockchains at the end of the simulation
    print('Node 1')
    print(node1.display_chain())
    print('Node 2')
    print(node2.display_chain())
    print('Node 3')
    print(node3.display_chain())
