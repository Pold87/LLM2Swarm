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
from controllers.groundsensor import ResourceVirtualSensor, Resource, GroundSensor
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
global notdonemod
notdonemod=False
startFlag = False

global txList, tripList, submodules
txList, tripList, submodules = [], [], []

global clocks, counters, logs, txs
clocks, counters, logs, txs = dict(), dict(), dict(), dict()


global estimate, totalWhite, totalBlack, byzantine

estimate =0
totalWhite =0
totalBlack=0

byzantine = 0
# /* Logging Levels for Console and File */
#######################################################################
import logging
loglevel = 10
logtofile = False 

# /* Experiment Global Variables */
#######################################################################

clocks['peering'] = Timer(5)
clocks['sensing'] = Timer(2)
clocks['block']   = Timer(120)
clocks['newround'] = Timer(45)
clocks['voting'] = Timer(30)

global geth_peer_count

GENESIS = Block(0, 0000, [], [gen_enode(i+1) for i in range(int(lp['environ']['NUMROBOTS']))], 0, 0, 0, nonce = 1, state = State())


####################################################################################################################################################################################
#### INIT STEP #####################################################################################################################################################################
####################################################################################################################################################################################

def init():
    global clocks,counters, logs, submodules, me, rw, nav, odo, gps, rb, w3, fsm, rs, erb, rgb,odo2,gs
    robotID = str(int(robot.variables.get_id()[2:])+1)
    robotIP = '127.0.0.1'
    robot.variables.set_attribute("id", str(robotID))
    robot.variables.set_attribute("byzantine_style", str(0))
    robot.variables.set_attribute("consensus_reached",str("false"))
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
    robot.log.info('Initialising Odo...')
    odo2 = Odometry(robot)
    
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

    # /* Init Ground sensor */
    robot.log.info('Initialising Ground sensor...')
    gs = GroundSensor(robot)
    
    # List of submodules --> iterate .start() to start all
    submodules = [erb,gs]

#########################################################################################################################
#### CONTROL STEP #######################################################################################################
#########################################################################################################################
global pos
pos = [0,0]
global last
last = 0
counter = 0
global checkt

def controlstep():
    global counter,last, pos, clocks, counters, startFlag, startTime,notdonemod,odo2,checkt, byzantine
    global estimate, totalWhite, totalBlack
    #startFlag = False 
    for clock in clocks.values():
         clock.time.step()
         checkt = clock.time.time_counter
    if not startFlag:
        ##########################
        #### FIRST STEP ##########
        ##########################
        #SPECIFY THE ROBOTS TO START AT TIME AFTER THEY HAVE MOVED
        if(int(me.id)<3 and checkt<51): # SPECIFY TIME TO START ROBOTS AND THEIR IDS	
            ##print("COMES HERE TO NOT JOIN", checkt)
            startFlag=False
            #if(notdonemod==False):
            #for module in submodules:
                    #try:
                    #    module.start()
                    #except:
                     #   robot.log.critical('Error Starting Module: %s', module)
                      #  sys.exit()
                #notdonemod=True
            #else:
                # Perform submodules step
                #for module in [erb, rs,rw]:
                    #module.step()
        else:


            startFlag=True
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
            #print(odo2.getPosition())
           # for clock in clocks.values():
           #     clock.reset()
            w3.start_tcp()
            w3.start_mining()
            #w3.sc.registerRobot()
            # Startup transactions
            #SPECIFY THE ROBOTS THAT ARE BYZANTINE
            if int(me.id) ==2 or int(me.id) == 2 or int(me.id) == 2 or int(me.id) == 5 or int(me.id) == 6 or int(me.id) == 3:
                byzantine = 1
            print("--//-- Registering robot --//--")
            txdata = {'function': 'registerRobot', 'inputs': []}
            tx = Transaction(sender = me.id, data = txdata)
            w3.send_transaction(tx)

    else:

        ###########################
        ######## ROUTINES #########
        ###########################

        def peering():
            global estimate, totalWhite, totalBlack, checkt, byzantine

            # Get the current peers from erb
            erb_enodes = {w3.gen_enode(peer.id) for peer in erb.peers}

            # Add peers on the toychain
            for enode in erb_enodes-set(w3.peers):
                try:
                    w3.add_peer(enode)

            
                    #Say Hello
                    #txdata = {'function': 'sendEstimate','inputs':[str(estimate)]}
                    #tx = Transaction(sender=me.id, data=txdata)
                    #w3.send_transaction(tx)
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
        for module in [erb, rs, rw, gs]:
            module.step()
            
        #TODO implement byzantine estimate
        #get estimate
        
        if byzantine ==1:# IF ROBOT IS BYZANTINE, THEY SEND WRONG ESTIMATE
            #print("Byzantine: ", me.id) 
            estimate = 0
        else:#Get value from the ground
            newValues = gs.getNew()
            for value in newValues:
                if value != 0:
                    totalWhite +=1
                else:
                    totalBlack+=1
            estimate = (0.5+totalWhite)/(totalBlack+totalWhite+1)
        myBlocksUBI = [0, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384]
        
        if clocks['newround'].query():#check after every interval timesteps
            #balance = w3.sc.getBalance(me.id)
            robbalance = w3.sc.getRobBalance(me.id)  #the balance of robots
            block    = w3.get_block('latest') #to get latest block heigh of robots
            receivedUBI= w3.sc.receivedUBI(me.id) #the total ubi it has received
            robotCount = w3.sc.getRobotCount() #how manybots
            newRound = w3.sc.isNewRound() #new round?
            doIhavePayouts = w3.sc.doIhavePayouts(me.id) #does the robot have any payouts
            getTotPayout = w3.sc.getTotPayout(me.id) #what is total payouts done
            #shouldIaskforUBI = w3.sc.doIhavePayouts(me.id)
            payout = w3.sc.getPayout(me.id)
            for i in range(len(myBlocksUBI)): #in those specific blocks, ask for ubi
            	if block.height == myBlocksUBI[i]:
            	    txdata1 = {'function': 'askForUBI', 'inputs': []}
            	    tx1 = Transaction(sender = me.id, data = txdata1)
            	    w3.send_transaction(tx1)
            balance = w3.sc.getBalance(me.id)
            print("Robot: ",me.id,"Payout: ", doIhavePayouts)
            
            
            if(doIhavePayouts):# if robot has payouts then get them
                txdata1 = {'function': 'askForPayout', 'inputs': []}
                tx1 = Transaction(sender = me.id, data = txdata1)
                w3.send_transaction(tx1)


            
            if(w3.sc.isNewRound() == True and robbalance > 0): #every new round update mean
                txdata = {'function': 'updateMean', 'inputs': []}
                tx = Transaction(sender = me.id, data = txdata)
                w3.send_transaction(tx) 
            print("Robot: ",me.id,"Time: " , checkt, "totPayout: ", getTotPayout, "robBalance: ",robbalance,
            "Tot UBI rec: ", receivedUBI, "Block height: ", block.height, "Robot count: ", robotCount,
            "New round: ", newRound)

            converged = w3.sc.isConverged()
            if converged: #check if converged
                mean = w3.sc.getMean()
                print("converged", mean)
                robot.variables.set_attribute("consensus_reached",str("true"))
            
            #if ubi != 0 and 
        if clocks['voting'].query():#after specific timetspes try to vote
            robbalance = w3.sc.getRobBalance(me.id)
    #        #if(me.id == '4'):
            if robbalance > 39:
                #print("before: ", balance)
                txdata = {'function': 'send_vote', 'inputs': [estimate]}
                tx = Transaction(sender = me.id, data = txdata)
                w3.send_transaction(tx)
                #print("after: ", balance)
          #  balance = w3.sc.getBalance(me.id)
            #if(me.id == '4'):

            
            
            




        # Perform clock steps
        for clock in clocks.values():
            #print(clock.time.time_counter)
            clock.time.step()

        if clocks['peering'].query():
            peering()

        w3.step()


        
        #if (counter % 100) == 0:
            
        #    print("Robot",me.id,"estimate is ", w3.sc.getEstimate())
        #counter +=1

        
        # Update blockchain state on the robot C++ object
        robot.variables.set_attribute("block", str(w3.get_block('last').height))
        robot.variables.set_attribute("block_hash", str(w3.get_block('last').hash))
        robot.variables.set_attribute("state_hash", str(w3.get_block('last').state.state_hash))


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
