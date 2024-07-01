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

global geth_peer_count

GENESIS = Block(0, 0000, [], [gen_enode(i+1) for i in range(int(lp['environ']['NUMROBOTS']))], 0, 0, 0, nonce = 1, state = State())


####################################################################################################################################################################################
#### INIT STEP #####################################################################################################################################################################
####################################################################################################################################################################################

def init():
    global clocks,counters, logs, submodules, me, rw, nav, odo, gps, rb, w3, fsm, rs, erb, rgb
    robotID = str(int(robot.variables.get_id()[2:])+1)
    robotIP = '127.0.0.1'
    robot.variables.set_attribute("id", str(robotID))
    robot.variables.set_attribute("scresources", "[]")
    robot.variables.set_attribute("foraging", "")
    robot.variables.set_attribute("state", "")
    robot.variables.set_attribute("quantity", "0")
    robot.variables.set_attribute("block", "")
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

#########################################################################################################################
#### CONTROL STEP #######################################################################################################
#########################################################################################################################
global pos
pos = [0,0]
global last
last = 0

counter = 0

def controlstep():
    global counter, last, pos, clocks, counters, startFlag, startTime


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

                    # Say hello!
                    txdata = {'function': 'sayHello', 'inputs': []}
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

        # Perform submodules step
        for module in [erb, rs, rw]:
            module.step()

        # Perform clock steps
        for clock in clocks.values():
            clock.time.step()

        if clocks['peering'].query():
            peering()

        w3.step()

        
        # Update blockchain state on the robot C++ object
        robot.variables.set_attribute("block", str(w3.get_block('last').height))
        robot.variables.set_attribute("block_hash", str(w3.get_block('last').hash))
        robot.variables.set_attribute("state_hash", str(w3.get_block('last').state.state_hash))

        #print("Clock is", clock.time)

        if (counter % 100) == 0:
            print("Robot", me.id, "helloCounter is ", w3.sc.getHelloCounter())

        counter += 1


def reset():
    pass

def destroy():
    if startFlag:
        w3.stop_mining()
        txs = w3.get_all_transactions()
        if len(txs) != len(set([tx.id for tx in txs])):
            print(f'REPEATED TRANSACTIONS ON CHAIN: #{len(txs)-len(set([tx.id for tx in txs]))}')

        for key, value in w3.sc.state.items():
            print(f"{key}: {value}")

        name   = 'sc.csv'
        header = ['TIMESTAMP', 'BLOCK', 'HASH', 'PHASH', 'BALANCE', 'TX_COUNT'] 
        logs['sc'] = Logger(f"{experimentFolder}/logs/{me.id}/{name}", header, ID = me.id)

        
        name   = 'block.csv'
        header = ['TELAPSED','TIMESTAMP','BLOCK', 'HASH', 'PHASH', 'DIFF', 'TDIFF', 'SIZE','TXS', 'UNC', 'PENDING', 'QUEUED']
        logs['block'] = Logger(f"{experimentFolder}/logs/{me.id}/{name}", header, ID = me.id)


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
