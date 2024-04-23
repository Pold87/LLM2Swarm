from hashlib import sha256

from toychain.src.Transaction import Transaction

def compute_hash(list):
    """
    Computes the hash of all the elements contained in the list by putting them in a string
    """
    if len(list) < 1:
        return
    hash_string = ""
    for elem in list:
        hash_string += str(elem)

    return sha256(hash_string.encode()).hexdigest()


def transaction_to_dict(transaction):
    return vars(transaction)

    # return {"source": transaction.source, "destination": transaction.destination, "data": transaction.data,
    #         "value": transaction.value, "timestamp": transaction.timestamp, "nonce": transaction.nonce,
    #         "id": transaction.id}


def dict_to_transaction(_dict):
    return Transaction(_dict["source"], _dict["destination"], _dict["value"], _dict["data"],_dict["timestamp"], _dict["nonce"], _dict["id"])

def block_to_list(block):
    """
    Translates a block in a list
    """
    data = []
    for t in block.data:
        data.append(transaction_to_dict(t))
    return [block.height, block.parent_hash, data, block.miner_id, block.timestamp, block.difficulty,
            block.total_difficulty, block.nonce, block.state.state_variables]


def create_block_from_list(_list):
    height = _list[0]
    parent_hash = _list[1]
    data = []
    for d in _list[2]:
        data.append(dict_to_transaction(d))
    miner_id = _list[3]
    timestamp = _list[4]
    difficulty = _list[5]
    total_difficulty = _list[6] - difficulty
    nonce = _list[7]
    state_variables = _list[8]

    return height, parent_hash, data, miner_id, timestamp, difficulty, total_difficulty, nonce, state_variables


class CustomTimer:
    def __init__(self):
        self.time_counter = 0

    def time(self):
        return self.time_counter

    # def sleep(self, period):
    #     starting_time = self.time()

    #     while self.time_counter < starting_time + period:
    #         sleep(0.01)

    def increase_timer(self):
        self.time_counter += 1

    def step(self):
        self.time_counter += 1

def gen_enode(id, host = '127.0.0.1', port = 0):
    if port == 0:
        port = 1233 + id
    return f"enode://{id}@{host}:{port}"