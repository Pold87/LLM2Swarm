import copy
import threading
from time import sleep

from toychain.src.constants import MEMPOOL_SYNC_INTERVAL, CHAIN_SYNC_INTERVAL, MEMPOOL_SYNC_TAG, CHAIN_SYNC_TAG
from toychain.src.utils import transaction_to_dict


# class ChainPinger(threading.Thread):
#     def __init__(self, node, interval=CHAIN_SYNC_INTERVAL):
#         super(ChainPinger, self).__init__()

#         self.node = node
#         self.message_handler = node.message_handler
#         self.node_server = node.node_server_thread
#         self.interval = interval

#         self.flag = threading.Event()

#     def run(self):
#         while not self.flag.is_set():
#             peer_list = copy.copy(self.node.peers) # To avoid iterating on a changing size object
#             try:
#                 for peer in peer_list:
#                     self.launch_sync(peer)

#                 self.node.custom_timer.sleep(self.interval)

#             except (ConnectionAbortedError, BrokenPipeError):
#                 pass

#             except Exception as e:
#                 self.flag.set()
#                 raise e


#     def stop(self):
#         self.flag.set()

#     def launch_sync(self, enode):
#         request = self.message_handler.construct_message("", CHAIN_SYNC_TAG, enode)
#         self.node_server.send_request(enode, request)


# class MemPoolPinger(threading.Thread):
#     def __init__(self, node, interval=MEMPOOL_SYNC_INTERVAL):
#         super(MemPoolPinger, self).__init__()

#         self.node = node
#         self.node_server = node.node_server_thread
#         self.message_handler = node.message_handler
#         self.interval = interval

#         self.flag = threading.Event()

#     def run(self):
#         while not self.flag.is_set():
#             peer_list = copy.copy(self.node.peers)  # To avoid iterating on a changing size object
#             try:
#                 for peer in peer_list:
#                     self.launch_sync(peer)

#                 self.node.custom_timer.sleep(self.interval)

#             except (ConnectionAbortedError, BrokenPipeError):
#                 pass

#             except Exception as e:
#                 self.flag.set()
#                 raise e

#     def stop(self):
#         self.flag.set()

#     def launch_sync(self, enode):
#         request = self.message_handler.construct_message("", MEMPOOL_SYNC_TAG, enode)
#         self.node_server.send_request(enode, request)

class ChainPinger():
    def __init__(self, node, interval=CHAIN_SYNC_INTERVAL):

        self.node = node
        self.message_handler = node.message_handler
        self.node_server = node.node_server_thread
        self.interval = interval

        self.flag  = False
        self.sleep = 0

    def run(self):
        peer_list = copy.copy(self.node.peers) # To avoid iterating on a changing size object
        try:
            for peer in peer_list:
                self.launch_sync(peer)

            self.sleep = self.interval + (int(self.node.id)+ int(self.node.custom_timer.time())) % 10

        except (ConnectionAbortedError, BrokenPipeError) as e:
            print(e)

        except Exception as e:
            self.stop()
            raise e
            
    def step(self):
        if self.flag:
            if self.sleep > 0:
                self.sleep -= 1
            else:
                self.run()

    def start(self):
        self.flag = True

    def stop(self):
        self.flag = False

    def launch_sync(self, enode):
        request = self.message_handler.construct_message("", CHAIN_SYNC_TAG, enode)
        self.node_server.send_request(enode, request)


class MemPoolPinger():
    def __init__(self, node, interval=MEMPOOL_SYNC_INTERVAL):
        self.node = node
        self.node_server = node.node_server_thread
        self.message_handler = node.message_handler
        self.interval = interval

        self.flag  = False
        self.sleep = 0

    def run(self):
        peer_list = copy.copy(self.node.peers)  # To avoid iterating on a changing size object
        try:
            for peer in peer_list:
                self.launch_sync(peer)

            self.sleep = self.interval + (int(self.node.id)+ int(self.node.custom_timer.time())) % 10

        except (ConnectionAbortedError, BrokenPipeError) as e:
            print(e)

        except Exception as e:
            self.stop()
            raise e

    def step(self):
        if self.flag:
            if self.sleep > 0:
                self.sleep -= 1
            else:
                self.run()

    def start(self):
        self.flag = True

    def stop(self):
        self.flag = False

    def launch_sync(self, enode):
        request = self.message_handler.construct_message("", MEMPOOL_SYNC_TAG, enode)
        self.node_server.send_request(enode, request)




