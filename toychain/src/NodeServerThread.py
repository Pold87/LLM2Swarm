import pickle
import threading

import socket
import time
import urllib.parse
from queue import Queue
from time import sleep

from toychain.src import constants
from toychain.src.MessageHandler import MessageHandler
from toychain.src.constants import ENCODING


class NodeServerThread(threading.Thread):
    """
    Thread answering to requests, every node has one
    """

    def __init__(self, node, host, port, id):
        super().__init__()

        self.sock = None
        self.id = id
        self.node = node
        self.host = host
        self.port = port
        self.max_packet = 0

        self.message_handler = MessageHandler(self)

        self.terminate_flag = threading.Event()

        print("Node " + str(self.id) + " starting on port " + str(self.port))

    def run(self):
        """
        Waiting for one other Node to connect
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

        while not self.terminate_flag.is_set():
            try:
                self.sock.settimeout(5)
                self.sock.listen(1)
                client_sock, client_address = self.sock.accept()
                self.handle_connection(client_sock)

            except socket.timeout:
                pass

            except Exception as e:
                raise e

            sleep(0.00001)

        self.sock.shutdown(True)
        self.sock.close()
        print("Node " + str(self.id) + " stopped")

    def handle_connection(self, sock):
        """
        Answer with the asked information
        """

        # Receive request
        data = sock.recv(4096)
        request = pickle.loads(data)

        # Send the answer
        answer = self.message_handler.handle_request(request)
        self.send(pickle.dumps(answer), sock)

    def send_request(self, enode, request):
        """
        Sends a request and returns the answer
        """
        parsed_enode = urllib.parse.urlparse(enode)
        address = (parsed_enode.hostname, parsed_enode.port)
        
        # Send the request
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(address)
            self.send(pickle.dumps(request), sock)

        except Exception as e:
            print(f"Error Connecting to Address : {address}")
            raise e
            
        # Get the answer
        data = self.receive(sock)
        try:
            answer = pickle.loads(data)
        except EOFError as e:
            print(data)
            raise e
        self.message_handler.handle_answer(answer)

        sock.close()

    def stop(self):
        self.terminate_flag.set()

    def send(self, data, sock):
        sock.sendall(data)
    

    def receive(self, sock):
        data = []
        packet = sock.recv(65536)
        if len(packet) > self.max_packet:
            # print('New max packet:', len(packet))
            self.max_packet = len(packet)
        data.append(packet)
        return b"".join(data)
