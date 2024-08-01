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

#from controllers.movement_clean import RandomWalk, Flocking
from controllers.movement import RandomWalk, GPS
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

import subprocess
import shutil

global startFlag
global notdonemod
notdonemod=False
startFlag = False

global txList, tripList, submodules
txList, tripList, submodules = [], [], []

global clocks, counters, logs, txs
clocks, counters, logs, txs = dict(), dict(), dict(), dict()


global estimate, totalWhite, totalBlack, byzantine, byzantine_style, log_folder
TPS = int(lp['environ']['TPS'])

estimate = []
totalWhite = 0
totalBlack= 0

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
clocks['ubi'] = Timer(100)
clocks['block']   = Timer(120)
clocks['newround'] = Timer(20)
clocks['voting'] = Timer(30)
global geth_peer_count

GENESIS = Block(0, 0000, [], [gen_enode(i+1) for i in range(int(lp['environ']['NUMROBOTS']))], 0, 0, 0, nonce = 1, state = State())



def init():
    global clocks,counters, logs, submodules, me, rw, nav, gps, rb, w3, fsm, rs, erb, rgb, gs, byzantine_style, log_folder, estimate
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
    robot.variables.set_attribute("response", "")

    # /* Initialize Console Logging*/
    #######################################################################
    log_folder = experimentFolder + '/new_log4_24rob_0byz/' + robotID + '/'

    # Monitor logs (recorded to file)
    name =  'monitor.log'
    os.makedirs(os.path.dirname(log_folder+name), exist_ok=True) 
    logging.basicConfig(filename=log_folder+name, filemode='w+', format='[{} %(levelname)s %(name)s] %(message)s'.format(robotID))
    logging.getLogger('sc').setLevel(10)
    logging.getLogger('w3').setLevel(10)
    logging.getLogger('poa').setLevel(10)
    robot.log = logging.getLogger()
    robot.log.setLevel(0)

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

    #rw = Flocking(robot, cp['scout_speed'])

    # # /* Init Navigation, __navigate process */
    # robot.log.info('Initialising navigation...')
    # nav = Navigate(robot, cp['recruit_speed'])
    
    # # /* Init odometry sensor */
    # robot.log.info('Initialising Odo...')
    # odo2 = Odometry(robot)
    
    # # /* Init odometry sensor */
    # robot.log.info('Initialising odometry...')
    # odo = OdoCompass(robot)

    # # /* Init GPS sensor */
    # robot.log.info('Initialising gps...')
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


    llm_output = 'controllers/outputs/' + str(myround) + "/" + str(robotID) + '.txt'
    if os.path.exists('controllers/outputs/'):
            shutil.rmtree('controllers/outputs/')
            os.makedirs('controllers/outputs/')

    start_output = "This is the first negotiation round, so there are no previous rounds."
    print("writing to ", llm_output)
    os.makedirs(os.path.dirname(llm_output), exist_ok=True)
    with open(llm_output, 'w') as file:
        file.write(start_output)

    estimate = []
        

        
global pos
pos = [0,0]
global last
last = 0
counter = 0
global checkt

global myround
myround = 0

def controlstep():
    global counter, last, pos, clocks, counters, startFlag, startTime, notdonemod, odo2, checkt, byzantine, byzantine_style, log_folder
    global estimate, totalWhite, totalBlack, robotID
    global myround

    robotID = str(int(robot.variables.get_id()[2:])+1)

    #startFlag = False 
    for clock in clocks.values():
         clock.time.step()
         checkt = clock.time.time_counter


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

    byzantine_style = int(robot.variables.get_attribute("byzantine_style"))

    for module in [erb, rs, rw, gs]:
        module.step()
            
    newValues = gs.getNew()
    #average = 0
    #for value in newValues:
    #    average += value
    #average = average / 3
    # Only append the center sensor
    current_position = gps.getPosition()
    estimate.append((newValues[1], current_position[0], current_position[1]))
        
    if ((counter + 1) % 500) == 0: 

        myround += 1

        # Read previous outputs (if it is not the first round)
        
        aggregated_content = ""

        if myround > 1:
            for m in range(myround - 1):
                for i in range(1,4): # TODO Change to number of robots
                    filepath = 'controllers/outputs/' + str(myround - 1) + "/" + str(i) + '.txt'
                    with open(filepath, 'r') as file:
                        llm_output = file.read()

                        # aggregated_content += f"Robot {i}\n\n{llm_output}\n\n"
                        #aggregated_content += "Robot " + str(i) + "\n\n" + llm_output + "\n\n"
                        aggregated_content += ""


        # Define the placeholders and their replacements
        placeholders = {
            '{robotID}': str(robotID),
            '{estimate}': ', '.join(str(x) for x in estimate),
            '{results}': aggregated_content,
            '{round}': str(myround)}

        print(totalWhite, totalBlack, estimate)


        if byzantine_style == 1: # Read the template for Byzantines
            mypath = 'controllers/byzmsg.txt'
        else: # Read the template for non-Byzantines
            mypath = 'controllers/mapmsg.txt'


        # Read the file contents
        with open(mypath, 'r') as file:
            msg = file.read()
        
        # Replace the placeholders in the prompt template
        for placeholder, replacement in placeholders.items():
            msg = msg.replace(placeholder, replacement)

        # Create the prompt for this robot
        myprompt = 'controllers/' + str(robotID) + '_prompt.txt'
        with open(myprompt, 'w') as file:
            os.makedirs(os.path.dirname(myprompt), exist_ok=True)
            file.write(msg)

        # Send the command to the LLM and retrieve the response
        mycommand = "python3 controllers/openai-api.py " + robotID         
        response = os.popen(mycommand).read()

        # print("My Byzantine style is ", byzantine_style)
        robot.variables.set_attribute("response", response)

        # Display the response using tkinter (can give errors like:
        # "Error: invalid literal for int() with base 10: 'twelfth'"
        # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #     s.connect(('localhost', 5000))
        #     myid = int(robotID) - 1
            
        #     message = str(myid) + " " + str(response) + "\n"
        #     #message = f"{myid} {response}\n"

        #     s.sendall(message.encode())

            
        print(response)

        # Save the LLM response of this robot in a file
        filepath = "controllers/outputs/" + str(myround) + "/" + robotID + ".txt" 
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'a') as file:
            file.write(response)

        estimate = []


    # Perform clock steps
    for clock in clocks.values():
        #print(clock.time.time_counter)
        clock.time.step()

    if clocks['peering'].query():
        peering()

    counter += 1

def reset():
    pass

def destroy():
    pass
