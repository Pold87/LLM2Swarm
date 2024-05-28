from random import randint
from json import loads as jsload
from copy import copy
from toychain.src.utils import compute_hash, transaction_to_dict
from os import environ

import logging
logger = logging.getLogger('sc')

class Block:
    """
    Class representing a block of a blockchain containing transactions
    """

    def __init__(self, height, parent_hash, data, miner_id, timestamp, difficulty, total_diff, nonce=None,
                 state_var=None, state = None):
        self.height = height
        self.number = height
        self.parent_hash = parent_hash
        self.data = data
        self.miner_id = miner_id
        self.timestamp = timestamp
        self.difficulty = difficulty
        self.total_difficulty = total_diff + difficulty

        if state:
            self.state = state
        else:
            self.state = State(state_var)

        self.nonce = nonce
        if nonce is None:
            self.nonce = randint(0, 1000)

        self.transactions_root = self.transactions_hash()
        self.hash = self.compute_block_hash()

    def compute_block_hash(self):
        """
        computes the hash of the block header
        :return: hash of the block
        """
        _list = [self.height, self.parent_hash, self.transactions_hash(), self.miner_id, self.timestamp,
                 self.difficulty,
                 self.total_difficulty, self.nonce]

        self.hash = compute_hash(_list)

        return self.hash

    def transactions_hash(self):
        """
        computes the hash of the block transactions
        :return: the hash of the transaction list
        """
        transaction_list = [transaction_to_dict(t) for t in self.data]
        self.transactions_root = compute_hash(transaction_list)
        return self.transactions_root

    def get_header_hash(self):
        header = [self.parent_hash, self.transactions_hash(), self.timestamp, self.difficulty, self.nonce]
        return compute_hash(header)

    def increase_nonce(self):  ###### POW
        self.nonce += 1

    def __repr__(self):
        """
        Translate the block object in a string object
        """
        return f"## H: {self.height}, D: {self.difficulty}, TD: {self.total_difficulty}, P: {self.miner_id}, BH: {self.hash[0:5]}, TS:{self.timestamp}, #T:{len(self.data)}, SH:{self.state.state_hash[0:5]}##"


class StateMixin:
    @property
    def getBalances(self):
        return self.balances
    
    @property
    def getN(self):
        return self.n
        
    @property
    def call(self):
        return None
    
    @property
    def state_variables(self):
        return {k: v for k, v in vars(self).items() if not (k.startswith('_') or k == 'msg' or k == 'block' or k == 'private')}
    
    @property
    def state(self):
        return {k: v for k, v in vars(self).items() if not (k.startswith('_') or k == 'msg' or k == 'block' or k == 'private')}

    @property
    def state_hash(self):
        return compute_hash(self.state.values())
    
    def apply_transaction(self, tx, block):

        self.msg = tx
        self.block = block

        self.balances.setdefault(tx.sender, 0)
        self.balances.setdefault(tx.receiver, 0)

        # Check sender funds
        if tx.value and self.balances[tx.sender] < tx.value:
            return
        
        # Apply the transfer of value
        self.balances[tx.sender] -= tx.value
        self.balances[tx.receiver] += tx.value
        
        # Apply the other functions contained in data
        self.n += 1

        if tx.data and 'function' in tx.data and 'inputs' in tx.data:
            function = getattr(self, tx.data.get("function"))
            inputs   = tx.data.get("inputs")
            try:
                function(*inputs) 
            except Exception as e:
                raise e

class State(StateMixin):

    def __init__(self, state_variables = None):

        if state_variables is not None:
            for var, value in state_variables.items(): setattr(self, var, value)     

        else:
            self.private     = {}
            self.n           = 0
            self.balances    = {}
            #self.robots      = {}
            self.mean = 0
            self.threshold = 0
            self.ticketPrice = 40
            self.tau = 0
            self.consensusReached = False
            self.startBlock = 0
            self.valueUBI = 20
            self.totalUBI = {}
            self.publicPayoutUBI = 0
            self.publicLength = 0
            self.roundCount = 0
            self.voteCount = 0
            self.voteOkCount = 0
            self.robotCount = 0
            self.lastUpdate = 0
            self.newRound = False
            self.blocksUBI = [0, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384]
            self.W_n = 0
            self.robotsToPay = []
            self.robot = {}
            self.round = {}

    def abs(self, x):
        if x < 0:
            return -x
        else:
            return x
    
    #def getBlockHeight(self):
    #    return self.block.height

    def getBalance(self,id): #return the self.balance for a robot
        try:
            return self.balances[id]
        except: 
            return 0
    def getRobBalance(self,id): #return new balance dict for a robot
        try:
            return self.robot[id]["robBalance"]
        except: 
            return 0
            
    def receivedUBI(self, id): #return total UBI received by a robots
        try:
            return self.robot[id]["totalUBI"]
        except:
            return 0

    def isConverged(self): #check convergence
        return self.consensusReached

    def isNewRound(self):
        return self.newRound

    def getMean(self): #retur mean
        return self.mean

    def getVoteCount(self):
        return self.voteCount

    def getVoteOkCount(self):
        return self.voteOkCount

    def getRobotCount(self):
        return self.robotCount

    def getTicketPrice(self):
        return self.ticketPrice
        
    def getRegisteredRobots(self): #get al robots registered
        return self.robot

    def doIhavePayouts(self,id): #check if a robot has payouts
        try:
            if (self.robot[id]["payout"])>0:
                return True
            else:
                return False
        except:
            return False
    def getPayout(self, id): #return the payout to do
        try:
            self.robot[id]["payout"]
        except:
            return 0
    def getTotPayout(self, id): #return all payouts done
        try:
            self.robot[id]["totalPayout"]
        except:
            return 0

    def amIregistered(self, id): #check if a robot has payouts
        try:
            if (id not in self.robot or not self.robot[id]["isRegistered"]):
                return False
            else:
                return True
        except:
            return False
    def getVoterCounter(self, id): #return all payouts done
        try:
            self.robot[id]["myVoteCounter"]
        except:
            return 0

    def registerRobot(self): #register a robot and initilaize all the variables that we need in a dict
        #print("Registered: ",self.msg.sender)
        self.publicLength = len(self.blocksUBI)
        self.ticketPrice = 40
        if self.msg.sender not in self.robot:
            self.robot[self.msg.sender] = {
                "robotAddress": self.msg.sender,
                "isRegistered": True,
                "payout": 0,
                "totalPayout": 0,
                "lastUBI": 0,
                "totalUBI": 0,
                "myVoteCounter": 0,
                "robBalance": 0
            }
            self.robotCount += 1
            
    def shouldIaskforUBI(self): #TODO function that robot checks to see if it transact askforUBI func
        pass
        


    def askForUBI(self): #get UBI payments - implemented based on SciRob
        if self.msg.sender not in self.robot or not self.robot[self.msg.sender]["isRegistered"]:
            print("Askig UBI Error: comes to not registered")
        else:
            myBlocksUBI = [0, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384]
            payoutUBI = 0
            myValueUBI = 20
            #print(self.robot)
            
            
            for i in range(len(myBlocksUBI)):
                if self.block.height < myBlocksUBI[i]:
                    payoutUBI = (i - self.robot[self.msg.sender]["lastUBI"]) * myValueUBI
                    self.robot[self.msg.sender]["lastUBI"] = i
                    self.robot[self.msg.sender]["totalUBI"] += payoutUBI
                    break

            if payoutUBI > 0:
                #print(payoutUBI)
                self.robot[self.msg.sender]["robBalance"] += payoutUBI
                #self.totalUBI += payoutUBI
                #print(self.balances[self.msg.sender])
            #return payoutUBI
        
    

    def askForPayout(self): #get payouts
        if self.msg.sender not in self.robot or not self.robot[self.msg.sender]["isRegistered"]:
            print("Payout error: Robot not registered")
        else:
            payout = self.robot[self.msg.sender]["payout"]
            print("Paying out the robots", self.msg.sender, payout )
            self.robot[self.msg.sender]["robBalance"] += payout #add payout to robots balance
            self.robot[self.msg.sender]["totalPayout"] += payout #add payout made to totalpayouts made
            #self.balances[self.msg.sender] += payout
            self.robot[self.msg.sender]["payout"] = 0 #reset payout to 0 until next mean
        #return payout

    def send_vote(self, estimate): #transaction to this function when  send estimate 
            if self.robot[self.msg.sender]["robBalance"] > 39: # if robots balance more that ticket price
                self.voteCount += 1
                if self.roundCount not in self.round: #save vote
                    self.round[self.roundCount] = []
                self.round[self.roundCount].append({
                "robot_address": self.msg.sender,
                "vote": round(estimate,3)
                })
                self.robot[self.msg.sender]["robBalance"] -= 40 # deduct tokens
                #print("round: ", self.robotCount, len(self.round[self.roundCount]))
                
                #if al robots voted , then new round
                if len(self.round[self.roundCount]) == self.robotCount and self.robotCount > 4: 
                    self.roundCount += 1
                    self.newRound = True
                    
                self.robot[self.msg.sender]["myVoteCounter"] += 1 #incrementvotes casted by robots

        #else:
            #print("Robot must pay the ticket price")


    def updateMean(self): #update the mean of tiles
        if self.msg.sender not in self.robot or not self.robot[self.msg.sender]["isRegistered"]:
            print("update Mean error: not registered")
        else:
            if self.lastUpdate >= self.roundCount:
                self.newRound = False
            else:
                oldMean = self.mean
                r = self.lastUpdate
                myThreshold = 0.2
                roundVoteOkCount = 0

                #check if vote within treshold to be counted
                for i in range(len(self.round[r])):
                    delta = float(self.round[r][i]["vote"] - self.mean)
                    #print(self.abs(delta))
                    if r == 0 or float(self.abs(delta)) < float(myThreshold):
                        self.voteOkCount += 1
                        roundVoteOkCount += 1
                        w_n = 1
                        self.W_n += w_n
                        self.mean += (w_n * delta) / self.W_n
                        self.robotsToPay.append(self.round[r][i]["robot_address"])
                #if none of the votes were ok, then consider all votes
                if roundVoteOkCount == 0:
                    for i in range(len(self.round[r])):
                        delta = float(self.round[r][i]["vote"] - self.mean)
                        self.voteOkCount += 1
                        roundVoteOkCount += 1
                        w_n = 1
                        self.W_n += w_n
                        self.mean += (w_n * delta) / self.W_n
                        self.robotsToPay.append(self.round[r][i]["robot_address"])

                # calculate the payouts to be given to robots whose votes were within threshold
                for b in range(len(self.robotsToPay)):
                    self.robot[self.robotsToPay[b]]["payout"] += 1 * self.ticketPrice * len(self.round[r]) / len(self.robotsToPay)
                    
                #TODO SHOULD WE EXPLICITLY SEND 40 TOKENS TO BE GIVEN BAKC THAT WERE ESCROWED FOR TRANSACTIONS

                #check for convergence
                myTau = 0.2 #is this correct? the paper says 0.2%
                if self.abs(oldMean - self.mean) < myTau and self.voteOkCount > 2 * self.robotCount:
                    self.consensusReached = True

                #reset variables
                self.lastUpdate += 1
                self.newRound = False
                #print(self.robotsToPay)
                self.robotsToPay = []

