from toychain.src import constants
from toychain.src.constants import MEMPOOL_SYNC_TAG, CHAIN_SYNC_TAG, BLOCK_REQUEST_TAG, DEBUG
from toychain.src.utils import dict_to_transaction, transaction_to_dict, block_to_list

import logging
logger = logging.getLogger('w3')

class MessageHandler:
    def __init__(self, node_server):
        self.node_server = node_server
        self.node = node_server.node
        self.enode = self.node.enode

    def handle_request(self, msg):
        """
        Returns a message containing the requested information
        """
        if not self.check_message_validity(msg):
            logger.error("invalid message")
            return

        if DEBUG:
            logger.debug(msg)

        msg_type = msg["type"]

        if msg_type == MEMPOOL_SYNC_TAG:
            transaction_list = list(self.node.mempool.values())
            content = []
            for t in transaction_list:
                content.append(transaction_to_dict(t))
            return self.construct_message(content, MEMPOOL_SYNC_TAG)

        elif msg_type == CHAIN_SYNC_TAG:
            last_block = self.node.get_block('last')
            content = (last_block.get_header_hash(), last_block.total_difficulty)
            return self.construct_message(content, CHAIN_SYNC_TAG)

        elif msg_type == BLOCK_REQUEST_TAG:
            content = self.handle_block_request(msg["data"])
            return self.construct_message(content, BLOCK_REQUEST_TAG)

    def handle_answer(self, msg):
        if not self.check_message_validity(msg):
            logger.error("invalid message")
            return

        if DEBUG:
            logger.debug(f"Node {self.node.id} received {msg}")

        msg_type = msg["type"]
        if msg_type == CHAIN_SYNC_TAG:
            self.handle_chain_sync_answer(msg)

        elif msg_type == MEMPOOL_SYNC_TAG:
            self.update_mempool(msg["data"])

        elif msg_type == BLOCK_REQUEST_TAG:
            self.handle_block_answer(msg)

    def check_message_validity(self, message):
        mandatory_keys = ["data", "type", "receiver", "sender"]
        if isinstance(message, dict):
            for key in mandatory_keys:
                if key not in message:
                    logger.error(f"Invalid key {message}")
                    return False
            return True
        logger.error(f"Invalid message {message}")
        return False

    def construct_message(self, data, msg_type, receiver=None):
        message = {"type": msg_type, "receiver": receiver, "sender": self.enode, "data": data}
        return message

    def update_mempool(self, transactions):
        _list = []
        for d in transactions:
            _list.append(dict_to_transaction(d))
        self.node.sync_mempool(_list)

    def handle_chain_sync_answer(self, message):
        last_block = self.node.get_block('last')
        if message["data"] == (last_block.get_header_hash(), last_block.total_difficulty):
            # Chains are synchronised
            if constants.DEBUG:
                logger.debug(f"Node {self.node.id} is chain sync")
            return

        if last_block.total_difficulty <= message["data"][1]:
            # If the chains have equal sizes, node keeps his
            # If the chain of the node is longer than the received one, let him do the work
            self.request_block(len(self.node.chain), message["sender"])
        else:
            if constants.DEBUG:
                logger.debug(f"Node {self.node.id} has a current diff of {last_block.total_difficulty}")

    def request_block(self, current_height, enode):
        """
        Sends the last 5 blocks header hash
        """
        content = []
        # Sends the block header + height of the last 5 blocks before the precised height
        for block in reversed(self.node.chain[max(0, current_height - 5):current_height]):
            content.append((block.get_header_hash(), block.height))

        request = self.construct_message(content, BLOCK_REQUEST_TAG, enode)
        self.node_server.send_request(enode, request)

    def handle_block_request(self, block_info_list):
        """
        Checks if one of the indicated blocks is in its chain
        """
        for block_info in block_info_list:
            block_header_hash = block_info[0]
            height = block_info[1]
            potential_common_block = self.node.get_block(height)
            if potential_common_block is None:
                return None, None
            if block_header_hash == potential_common_block.get_header_hash():
                # Common block found
                partial_chain = []
                i = height + 1
                while i < len(self.node.chain):
                    partial_chain.append(block_to_list(self.node.get_block(i)))
                    i += 1
                return height, partial_chain
        return height, None

    def handle_block_answer(self, msg):
        data = msg["data"]
        height = data[0]
        chain = data[1]

        if height is None:
            return

        if chain is None:
            self.request_block(height, msg["sender"])
        elif len(chain) > 0:
            self.node.sync_chain(chain, height)
