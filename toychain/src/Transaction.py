from uuid import uuid4

class Transaction:
    def __init__(self, sender, receiver = 0, value = 0, data={}, timestamp=None, nonce=None, id=None):
        self.source = str(sender)
        self.sender = str(sender)

        self.destination = str(receiver)
        self.receiver    = str(receiver)

        self.value = value

        self.data = data

        self.timestamp = timestamp
        self.nonce = nonce
        self.id = id
        if not id:
            self.id = str(uuid4())

    def __str__(self):
        return f"hash: {self.id}, to: {self.receiver}, from: {self.sender}, value: {self.value}"