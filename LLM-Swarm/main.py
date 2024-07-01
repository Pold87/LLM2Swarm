#!/usr/bin/env python3
# This is the main control loop running in each argos robot

# /* Import Packages */
#######################################################################
import random, math
import time, sys, os

import json
experimentFolder = os.environ['EXPERIMENTFOLDER']
sys.path += [os.environ['MAINFOLDER'], \
             os.environ['EXPERIMENTFOLDER']+'/controllers', \
             os.environ['EXPERIMENTFOLDER']
            ]

from controllers.movement import RandomWalk, Navigate, Odometry, OdoCompass, GPS
from controllers.groundsensor import ResourceVirtualSensor, Resource
from controllers.erandb import ERANDB
from controllers.rgbleds import RGBLEDs
from controllers.aux import *
from controllers.aux import Timer
from controllers.statemachine import *

from controllers.control_params import params as cp
from loop_functions.loop_params import params as lp

from toychain.src.Node import Node
from toychain.src.Block import Block, State
from toychain.src.utils import gen_enode

from toychain.src.consensus.ProofOfAuth import ProofOfAuthority
from toychain.src.Transaction import Transaction

# /* Global Variables */
#######################################################################
global robot

global startFlag
startFlag = False

global txList, tripList, submodules
txList, tripList, submodules = [], [], []

global clocks, counters, logs, txs
clocks, counters, logs, txs = dict(), dict(), dict(), dict()

# /* Logging Levels for Console and File */
#######################################################################
import logging
loglevel = 10
logtofile = False 

# /* Experiment Global Variables */
#######################################################################

clocks['peering'] = Timer(5)
clocks['sensing'] = Timer(2)
clocks['block']   = Timer(150)

# Store the position of the market and cache
market   = Resource({"x":lp['market']['x'], "y":lp['market']['y'], "radius": lp['market']['r']})
cache    = Resource({"x":lp['cache']['x'], "y":lp['cache']['y'], "radius": lp['cache']['r']})

global geth_peer_count

GENESIS = Block(0, 0000, [], [gen_enode(i+1) for i in range(int(lp['environ']['NUMROBOTS']))], 0, 0, 0, nonce = 1, state = State())

class ResourceBuffer(object):
    """ Establish the resource buffer class 
    """
    def __init__(self, ageLimit = 2):
        """ Constructor
        :type id__: str
        :param id__: id of the peer
        """
        # Add the known peer details
        self.buffer = []
        self.ageLimit = ageLimit
        self.best = None

    def getJSON(self, resource):
        return resource._json

    def getJSONs(self, idx = None):
        return {self.getJSON(res) for res in self.buffer}

    def addResource(self, new_res, update_best = False):
        """ This method is called to add a new resource
        """   
        if isinstance(new_res, str):
            new_res = Resource(new_res)

        # Is in the buffer? NO -> Add to buffer
        if (new_res.x, new_res.y) not in self.getLocations():
            res = new_res
            self.buffer.append(res)
            robot.log.info("Added: %s; Total: %s " % (res._desc, len(self)))

        # Is in the buffer? YES -> Update buffer
        else:
            res = self.getResourceByLocation((new_res.x, new_res.y))

            # if new_res.quantity < res.quantity or new_res._timeStamp > res._timeStamp:
            if new_res.quantity < res.quantity:
                res.quantity = new_res.quantity
                res._timeStamp = new_res._timeStamp
                # robot.log.info("Updated resource: %s" % self.getJSON(res))

        if update_best:
            self.best = self.getResourceByLocation((new_res.x, new_res.y))

        return res

    def removeResource(self, resource):
        """ This method is called to remove a peer Id
            newPeer is the new peer object
        """   
        self.buffer.remove(resource)
        robot.log.info("Removed resource: "+self.getJSON(resource))

    def __len__(self):
        return len(self.buffer)

    def sortBy(self, by = 'value', inplace = True):

        if inplace:
            if by == 'timeStamp':
                pass
            elif by == 'value':
                self.buffer.sort(key=lambda x: x.utility, reverse=True)
        else:
            return self.buffer.sort(key=lambda x: x.utility, reverse=True)

    def getLocations(self):
        return [(res.x, res.y) for res in self.buffer]

    def getDistances(self, x, y):
        return [math.sqrt((x-res.x)**2 + (y-res.y)**2) for res in self.buffer]

    def getResourceByLocation(self, location):
        return self.buffer[self.getLocations().index(location)]


class Trip(object):

    def __init__(self, patch):
        self.tStart = w3.custom_timer.time()
        self.FC     = 0
        self.Q      = 0
        self.C      = []
        self.MC     = []
        self.TC     = 0
        self.ATC    = 0
        self.price = patch['util']*patch['epoch']['price']
        self.finished = False
        # self.price = 1000
        tripList.append(self)

    @property
    def timedelta(self):
        timedelta = w3.custom_timer.time() - self.tStart
        return round(timedelta, 2)

    def update(self, Q):
        finished = False

        if self.FC == 0:
            self.FC = self.timedelta

        C  = self.timedelta-self.FC
        
        if len(self.C) > 0 and C-self.C[-1] > 1.25*self.price:
            robot.log.info("Finished before collection %s" % (C-self.C[-1]))
            finished = True

        if int(Q) > self.Q:
            finished = False
            # patch  = tcp_sc.request(data = 'getPatch')
            # self.price = patch['util']*patch['epoch']['price']
            self.Q = int(Q)
            self.C.append(C)

            if len(self.C) > 1:
                MC = self.C[-1]-self.C[-2]
                robot.log.info("Collected %i // MC: %i" % (self.Q, MC))
                self.MC.append(MC)

                if MC > self.price:
                    finished = True

            self.TC  = self.timedelta
            self.ATC = round(self.TC/self.Q)
            self.profit  = round(self.Q*self.price-self.TC)

        self.finished = finished
        return finished

    def __str__(self):
        C  = str(self.C).replace(' ','')
        MC = str(self.MC).replace(' ','')
        return "%i %i %i %s %s %i %i %i" % (self.tStart, self.FC, self.Q, C, MC, self.TC, self.ATC, self.profit)        

####################################################################################################################################################################################
#### INIT STEP #####################################################################################################################################################################
####################################################################################################################################################################################

def init():
    global clocks,counters, logs, submodules, me, rw, nav, odo, gps, rb, w3, fsm, rs, erb, rgb
    robotID = str(int(robot.variables.get_id()[2:])+1)
    robotIP = '127.0.0.1'
    robot.variables.set_attribute("id", str(robotID))
    robot.variables.set_attribute("circle_color", "gray50")
    robot.variables.set_attribute("scresources", "[]")
    robot.variables.set_attribute("foraging", "")
    robot.variables.set_attribute("dropResource", "")
    robot.variables.set_attribute("hasResource", "")
    robot.variables.set_attribute("resourceCount", "0")
    robot.variables.set_attribute("state", "")
    robot.variables.set_attribute("forageTimer", "0")
    robot.variables.set_attribute("quantity", "0")
    robot.variables.set_attribute("block", "")
    robot.variables.set_attribute("groupSize", "1")
    robot.variables.set_attribute("block", "0")
    robot.variables.set_attribute("hash", str(hash("genesis")))
    robot.variables.set_attribute("state_hash", str(hash("genesis")))

    # /* Initialize Console Logging*/
    #######################################################################
    log_folder = experimentFolder + '/logs/' + robotID + '/'

    # Monitor logs (recorded to file)
    name =  'monitor.log'
    os.makedirs(os.path.dirname(log_folder+name), exist_ok=True) 
    logging.basicConfig(filename=log_folder+name, filemode='w+', format='[{} %(levelname)s %(name)s] %(message)s'.format(robotID))
    logging.getLogger('sc').setLevel(20)
    logging.getLogger('w3').setLevel(70)
    logging.getLogger('poa').setLevel(70)
    robot.log = logging.getLogger()
    robot.log.setLevel(10)

    # /* Initialize submodules */
    #######################################################################
    # # /* Init web3.py */
    robot.log.info('Initialising Python Geth Console...')
    w3 = Node(robotID, robotIP, 1233 + int(robotID), ProofOfAuthority(GENESIS))

    # /* Init an instance of peer for this Pi-Puck */
    me = Peer(robotID, robotIP, w3.enode, w3.key)

    # /* Init an instance of the buffer for resources  */
    robot.log.info('Initialising resource buffer...')
    rb = ResourceBuffer()

    # /* Init E-RANDB __listening process and transmit function
    robot.log.info('Initialising RandB board...')
    erb = ERANDB(robot, cp['erbDist'] , cp['erbtFreq'])

    #/* Init Resource-Sensors */
    robot.log.info('Initialising resource sensor...')
    rs = ResourceVirtualSensor(robot)
    
    # /* Init Random-Walk, __walking process */
    robot.log.info('Initialising random-walk...')
    rw = RandomWalk(robot, cp['scout_speed'])

    # /* Init Navigation, __navigate process */
    robot.log.info('Initialising navigation...')
    nav = Navigate(robot, cp['recruit_speed'])

    # /* Init odometry sensor */
    robot.log.info('Initialising odometry...')
    odo = OdoCompass(robot)

    # /* Init GPS sensor */
    robot.log.info('Initialising gps...')
    gps = GPS(robot)

    # /* Init LEDs */
    rgb = RGBLEDs(robot)

    # /* Init Finite-State-Machine */
    fsm = FiniteStateMachine(robot, start = States.IDLE)

    # List of submodules --> iterate .start() to start all
    submodules = [erb]

    # /* Initialize logmodules*/
    #######################################################################
    # Experiment data logs (recorded to file)
    # name   = 'resource.csv'
    # header = ['COUNT']
    # logs['resources'] = Logger(log_folder+name, header, rate = 5, ID = me.id)

    # name   = 'firm.csv'
    # header = ['TSTART', 'FC', 'Q', 'C', 'MC', 'TC', 'ATC', 'PROFIT']
    # logs['firm'] = Logger(log_folder+name, header, ID = me.id)

    # name   = 'epoch.csv'
    # header = ['RESOURCE_ID', 'NUMBER', 'BSTART', 'Q', 'TC', 'ATC', 'price']
    # # header =w3.sc.functions.Epoch_key().call()
    # logs['epoch'] = Logger(log_folder+name, header, ID = me.id)

    # name   = 'robot_sc.csv'
    # header = ["isRegistered", "efficiency", "income", "balance", "task"]
    # # header = w3.sc.functions.Robot_key().call()
    # logs['robot_sc'] = Logger(log_folder+name, header, ID = me.id)

    # name   = 'fsm.csv'
    # header = stateList
    # logs['fsm'] = Logger(log_folder+name, header, rate = 10, ID = me.id)

    # name   =  'odometry.csv'
    # header = ['DIST']
    # logs['odometry'] = Logger(log_folder+name, header, rate = 10, ID = me.id)

    txs['sell'] = None
    txs['buy']  = None
    txs['drop'] = None

#########################################################################################################################
#### CONTROL STEP #######################################################################################################
#########################################################################################################################
global pos
pos = [0,0]
global last
last = 0
global last_leave_decision_epoch
last_leave_decision_epoch = 0
global last_join_decision_epoch
last_join_decision_epoch = 0


def controlstep():
    global last, pos, clocks, counters, startFlag, startTime

    if not startFlag:
        ##########################
        #### FIRST STEP ##########
        ##########################

        startFlag = True 
        startTime = 0

        robot.log.info('--//-- Starting Experiment --//--')

        for module in submodules:
            try:
                module.start()
            except:
                robot.log.critical('Error Starting Module: %s', module)
                sys.exit()

        for log in logs.values():
            log.start()

        for clock in clocks.values():
            clock.reset()

        # Startup transactions

        txdata = {'function': 'register', 'inputs': []}
        tx = Transaction(sender = me.id, data = txdata)
        w3.send_transaction(tx)

        res = robot.variables.get_attribute("newResource")

        if res:
            print(res)
            txdata = {'function': 'updatePatch', 'inputs': Resource(res)._calldata}
            tx = Transaction(sender = me.id, receiver = 2, value = 0, data = txdata, nonce = last, timestamp = w3.custom_timer.time())
            w3.send_transaction(tx)

            # w3.sc.functions.updatePatch(*resource._calldata).transact()

        # my_eff = int(float(robot.variables.get_attribute("eff"))*100)
        txdata = {'function': 'register', 'inputs': []}
        tx = Transaction(sender = me.id, data = txdata)
        w3.send_transaction(tx)

        w3.start_tcp()
        w3.start_mining()
    else:

        ###########################
        ######## ROUTINES #########
        ###########################

        def peering():

            # Get the current peers from erb
            erb_enodes = {w3.gen_enode(peer.id) for peer in erb.peers}

            # Add peers on the toychain
            for enode in erb_enodes-set(w3.peers):
                try:
                    w3.add_peer(enode)
                    
                    #Say hello!
                    txdata = {'function':'sayHello','inputs':[]}
                    tx = Transaction(sender = me.id, data = txdata)
                    w3.send_transaction(tx)
                    
                except Exception as e:
                    raise e
                
            # Remove peers from the toychain
            for enode in set(w3.peers)-erb_enodes:
                try:
                    w3.remove_peer(enode)
                except Exception as e:
                    raise e

            # Turn on LEDs according to geth peer count
            rgb.setLED(rgb.all, rgb.presets.get(len(w3.peers), 3*['red']))

        def homing():

            # Navigate to the market
            arrived = True

            if nav.get_distance_to(market._pr) < 0.9*market.radius:           
                nav.avoid(move = True)
                
            elif nav.get_distance_to(market._pr) < market.radius and len(w3.peers) > 1:
                nav.avoid(move = True)

            else:
                nav.navigate_with_obstacle_avoidance(market._pr)
                arrived = False

            return arrived

        def dropping(resource):

            direction = (resource._pv-market._pv).rotate(-25, degrees = True).normalize()
            target = direction*(market.radius+cache.radius)/2+market._pv

            # Navigate to drop location
            arrived = True

            if nav.get_distance_to(market._p) < market.radius + 0.5* (cache.radius-market.radius):
                nav.avoid(move = True)
            else:
                nav.navigate_with_obstacle_avoidance(target)
                arrived = False

            return arrived

        def grouping(resource):

            direction = (resource._pv-market._pv).rotate(25, degrees = True).normalize()
            target = direction*(market.radius+cache.radius)/2+market._pv

            # Navigate to the group location
            arrived = True
            if nav.get_distance_to(target) < 0.2*market.radius:           
                nav.avoid(move = True) 
            else:
                nav.navigate(target)
                arrived = False

            return arrived

        def sensing(global_pos = True):

            # Sense environment for resources
            if clocks['sensing'].query(): 
                res = rs.getNew()

                if res:
                    if global_pos:
                        # Use resource with GPS coordinates
                        rb.addResource(res)

                    else:
                        # Add odometry error to resource coordinates
                        error = odo.getPosition() - gps.getPosition()
                        res.x += error.x
                        res.y += error.y

                        # use resource with odo coordinates
                        rb.addResource(Resource(res._json))

                    return res

        def decision(patch):
            
            last_epoch = patch['allepochs'][-1]
            print(last_epoch)
            # Average profit is the cost of one resource times the average of the ATCs
            AP = patch['util']*last_epoch['price'] - sum(last_epoch['ATC'])/len(last_epoch['ATC'])
        
            # Linear decision probability
            P = cp['firm']['entry_K']/10 * 1/(patch['util']*last_epoch['price']) * AP
            
            # Saturate for low profits
            if abs(AP) < 0.075 * patch['util']*last_epoch['price']:
                P = 0

            robot.log.info(f"AP @ {patch['qlty']}: {round(AP)}")
            robot.log.info(f"Entry/exit: {round(100*P, 1)}%")

            if random.random() < abs(P):
                if P < 0:
                    return 'exit'
                else:
                    return 'entry'
            else:
                return None

        ##############################
        ##### STATE-MACHINE STEP #####
        ##############################

        #########################################################################################################
        #### State::EVERY
        #########################################################################################################
        
        # Perform submodules step
        for module in [erb, rs, odo]:
            module.step()

        # Perform clock steps
        for clock in clocks.values():
            clock.time.step()

        # # Perform file logging step
        # if logs['resources'].query():
        #     logs['resources'].log([len(rb)])

        # if logs['fsm'].query():
        #     logs['fsm'].log([round(fsm.accumTime[state], 3) if state in fsm.accumTime else 0 for state in stateList ])

        # robot.variables.set_attribute("odo_position",repr(odo.getPosition()))

        if clocks['peering'].query():
            peering()

        w3.step()
        
        if(counter % 100) == 0:
            print("Robot", me.id, "helloCounter is", w3.sc.getHelloCounter())
        counter +=1

        # Update blockchain state on the robot C++ object
        robot.variables.set_attribute("block", str(w3.get_block('last').height))
        robot.variables.set_attribute("block_hash", str(w3.get_block('last').hash))
        robot.variables.set_attribute("state_hash", str(w3.get_block('last').state.state_hash))

        # Get perfect position if at nest
        if robot.variables.get_attribute("at") == "cache":
            odo.setPosition()

        #########################################################################################################
        #### State::IDLE
        #########################################################################################################
        if fsm.query(States.IDLE):

            fsm.setState(States.PLAN, message = "Planning")

        #########################################################################################################
        #### State::PLAN  
        ######################################################################################################### 

        elif fsm.query(States.PLAN):
            global last_leave_decision_epoch, last_join_decision_epoch

            my_patch = w3.sc.getMyPatch(me.id)
            
            if my_patch:

                if last_leave_decision_epoch < my_patch['epoch']['start']:
                    print('New epoch on my patch')
                    last_leave_decision_epoch = my_patch['epoch']['start']

                    if decision(my_patch) == 'exit':
                        res = Resource(my_patch['json'])
                        fsm.setState(States.TRANSACT, message = "Leaving: %s" % res._desc, pass_along = {'function': 'leavePatch', 'inputs': []})

                else:
                    rb.addResource(my_patch['json'], update_best = True)
                    fsm.setState(States.HOMING, message = None)

            else:
                
                last_epoch, last_patch = w3.sc.getEpoch()
                if last_epoch and last_join_decision_epoch < last_epoch['start']:
                    print(f"New epoch on {last_patch['qlty']}")
                    last_join_decision_epoch = last_epoch['start']

                    if decision(last_patch) == 'entry':
                        res = Resource(last_patch['json'])
                        fsm.setState(States.TRANSACT, message = "Joining: %s" % res._desc, pass_along = {'function': 'joinPatch', 'inputs': res._calldata[:2]})
                    else:
                        homing()
                else:
                    homing()

        #########################################################################################################
        #### State::HOMING  
        #########################################################################################################

        elif fsm.query(States.HOMING):

            arrived = grouping(rb.best)

            if arrived:
                
                my_patch = w3.sc.getMyPatch(me.id)
                block    = w3.get_block('latest')

                if my_patch:
                    rb.addResource(my_patch['json'], update_best = True)

                    if block.height >= my_patch['epoch']['start']+2 and str(me.id) not in my_patch['epoch']['robots']: 
                        Trip(my_patch)
                        fsm.setState(States.FORAGE, message = 'Foraging: %s' % (rb.best._desc))
                else:
                    fsm.setState(States.PLAN, message = None)

            if clocks['block'].query():
                fsm.setState(States.PLAN, message = None)

        #########################################################################################################
        #### State::FORAGE
        #########################################################################################################
        elif fsm.query(States.FORAGE):

            myPatch = w3.sc.getMyPatch(me.id)

            if myPatch == None or myPatch == "" or myPatch == []:
                fsm.setState(States.PLAN, message = "Falsely foraging")

            else:

                # Distance to resource
                distance = nav.get_distance_to(rb.best._pr)

                # Resource virtual sensor
                resource = sensing()
                found = resource and resource._p == rb.best._p
                finished = False

                if found:
                    rb.best = resource

                if found and distance < 0.9*rb.best.radius:
                    robot.variables.set_attribute("foraging", "True")
                    nav.avoid(move = True)

                    finished = tripList[-1].update(robot.variables.get_attribute("quantity"))

                    # if int(robot.variables.get_attribute("quantity")) >= cp['max_Q']:
                    #     finished = True

                else:
                    nav.navigate_with_obstacle_avoidance(rb.best._pr)

                ### SHORT-RUN DECISION MAKING
                if finished:
                    robot.variables.set_attribute("foraging", "")

                    # # Log the result of the trip
                    # logs['firm'].log([*str(tripList[-1]).split()])

                    fsm.setState(States.DROP, message = "Collected %s // Profit: %s" % (tripList[-1].Q, round(tripList[-1].profit,2)))

        #########################################################################################################
        #### State::DROP
        #########################################################################################################
        elif fsm.query(States.DROP):

            # Navigate home
            arrived = dropping(rb.best)

            if arrived:

                # Transact to drop resource
                if not txs['drop']:
                    robot.log.info(f"Dropping. FC:{tripList[-1].FC} TC:{tripList[-1].TC} ATC:{tripList[-1].ATC}")
                    txdata = {'function': 'dropResource', 'inputs': rb.best._calldata+(tripList[-1].Q, tripList[-1].TC)}
                    txs['drop'] = Transaction(sender = me.id, data = txdata, timestamp = w3.custom_timer.time())
                    w3.send_transaction(txs['drop'])
   
                # Transition state  
                else:
                    if w3.get_transaction_receipt(txs['drop'].id):
                        robot.variables.set_attribute("dropResource", "True")

                        if not robot.variables.get_attribute("hasResource"):
                            txs['drop'] = None
                            robot.variables.set_attribute("dropResource", "")   
                            fsm.setState(States.PLAN, message = "Dropped: %s" % rb.best._desc)                       

        #########################################################################################################
        #### State::TRANSACT  
        #########################################################################################################

        elif fsm.query(States.TRANSACT):

            homing()

            if not txs['buy']:

                txdata = fsm.pass_along
                txs['buy'] = Transaction(sender = me.id, data = txdata, timestamp = w3.custom_timer.time())
                w3.send_transaction(txs['buy'])

            if w3.get_transaction_receipt(txs['buy'].id):

                txs['buy'] = None
                fsm.setState(States.PLAN, message = "Transaction success")

#########################################################################################################################
#### RESET-DESTROY STEPS ################################################################################################
#########################################################################################################################

def reset():
    pass

def destroy():
    if startFlag:
        # w3.geth.miner.stop()
        w3.stop_mining()
        # w3.display_chain()
        txs = w3.get_all_transactions()
        if len(txs) != len(set([tx.id for tx in txs])):
            print(f'REPEATED TRANSACTIONS ON CHAIN: #{len(txs)-len(set([tx.id for tx in txs]))}')

        for key, value in w3.sc.state.items():
            print(f"{key}: {value}")

        name   = 'sc.csv'
        header = ['TIMESTAMP', 'BLOCK', 'HASH', 'PHASH', 'BALANCE', 'TX_COUNT'] 
        logs['sc'] = Logger(f"{experimentFolder}/logs/{me.id}/{name}", header, ID = me.id)

        name   = 'firm.csv'
        header = ['TSTART', 'FC', 'Q', 'C', 'MC', 'TC', 'ATC', 'PROFIT']
        logs['firm'] = Logger(f"{experimentFolder}/logs/{me.id}/{name}", header, ID = me.id)

        name   = 'epoch.csv'
        header = ['RESOURCE_ID', 'NUMBER', 'BSTART', 'Q', 'TC', 'ATC', 'price', 'robots', 'TQ', 'AATC', 'AP']
        logs['epoch'] = Logger(f"{experimentFolder}/logs/{me.id}/{name}", header, ID = me.id)
        
        name   = 'block.csv'
        header = ['TELAPSED','TIMESTAMP','BLOCK', 'HASH', 'PHASH', 'DIFF', 'TDIFF', 'SIZE','TXS', 'UNC', 'PENDING', 'QUEUED']
        logs['block'] = Logger(f"{experimentFolder}/logs/{me.id}/{name}", header, ID = me.id)

        # Log the result of the each trip performed by robot
        for trip in tripList:
            if trip.finished:
                logs['firm'].log([*str(trip).split()])

        # Log each epoch over the operation of the swarm
        epochs = w3.sc.getAllEpochs()
        for resource_id, resource_epochs in epochs.items():
            for epoch in resource_epochs:
                logs['epoch'].log([resource_id]+[str(x).replace(" ","") for x in epoch.values()])

        # Log each block over the operation of the swarm
        blockchain = w3.chain
        for block in blockchain:
            logs['block'].log(
                [w3.custom_timer.time()-block.timestamp, 
                block.timestamp, 
                block.height, 
                block.hash, 
                block.parent_hash, 
                block.difficulty,
                block.total_difficulty, 
                sys.getsizeof(block) / 1024, 
                len(block.data), 
                0
                ])
            
            logs['sc'].log(
                [block.timestamp, 
                block.height, 
                block.hash, 
                block.parent_hash, 
                block.state.balances.get(me.id,0),
                block.state.n
                ])

        
    print('Killed robot '+ me.id)

#########################################################################################################################
#########################################################################################################################
#########################################################################################################################


def getEnodes():
    return [peer['enode'] for peer in w3.geth.admin.peers()]

def getEnodeById(__id, gethEnodes = None):
    if not gethEnodes:
        gethEnodes = getEnodes() 

    for enode in gethEnodes:
        if readEnode(enode, output = 'id') == __id:
            return enode

def getIds(__enodes = None):
    if __enodes:
        return [enode.split('@',2)[1].split(':',2)[0].split('.')[-1] for enode in __enodes]
    else:
        return [enode.split('@',2)[1].split(':',2)[0].split('.')[-1] for enode in getEnodes()]






















        #########################################################################################################
        #### Scout.EXPLORE
        #########################################################################################################

        # elif fsm.query(Scout.EXPLORE):

        #     if clocks['block'].query():

        #         # Confirm I am still scout
        #         fsm.setState(States.PLAN, message = None)

        #     else:

        #         # Perform a random-walk 
        #         rw.step()

        #         # Look for resources
        #         sensing()

        #         # Transition state
        #         if clocks['explore'].query(reset = False):

        #             # Sucess exploration: Sell
        #             if rb.buffer:
        #                 fsm.setState(Scout.SELL, message = "Found %s" % len(rb))

        #             # Unsucess exploration: Buy
        #             else:
        #                 clocks['buy'].reset()
        #                 fsm.setState(States.ASSIGN, message = "Found %s" % len(rb))


        #########################################################################################################
        #### Scout.SELL
        #########################################################################################################

        # elif fsm.query(Scout.SELL):

        #     # Navigate to market
        #     if fsm.query(Recruit.HOMING, previous = True):
        #         homing(to_drop = True)
        #     else:
        #         homing()

        #     # Sell resource information  
        #     if rb.buffer:
        #         resource = rb.buffer.pop(-1)
        #         print(resource._calldata)
        #         sellHash = w3.sc.functions.updatePatch(*resource._calldata).transact()
        #         txs['sell'] = Transaction(sellHash)
        #         robot.log.info('Selling: %s', resource._desc)

        #     # Transition state  
        #     else:
        #         if txs['sell'].query(3):
        #             txs['sell'] = Transaction(None)
        #             fsm.setState(States.ASSIGN, message = "Sell success")

        #         elif txs['sell'].fail == True:    
        #             txs['sell'] = Transaction(None)
        #             fsm.setState(States.ASSIGN, message = "Sell failed")

        #         elif txs['sell'].hash == None:
        #             fsm.setState(States.ASSIGN, message = "None to sell")
