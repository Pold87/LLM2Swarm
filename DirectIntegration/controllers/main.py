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

from controllers.movement import RandomWalk, Navigate
from controllers.movement import GPS
from controllers.groundsensor import ResourceVirtualSensor, Resource, GroundSensor
from controllers.erandb import ERANDB
from controllers.rgbleds import RGBLEDs
from controllers.aux import *
from controllers.aux import Timer
from controllers.statemachine import *

from controllers.control_params import params as cp
from loop_functions.loop_params import params as lp


# /* Global Variables */
#######################################################################
global robot

import subprocess
import shutil
import re

global startFlag
startFlag = False

global txList, tripList, submodules
txList, tripList, submodules = [], [], []

global clocks, counters, logs, txs
clocks, counters, logs, txs = dict(), dict(), dict(), dict()


global estimate, totalWhite, totalBlack, byzantine, byzantine_style, log_folder, target
TPS = int(lp['environ']['TPS'])

target = [0.83, -1.05]

estimate = []
totalWhite = 0
totalBlack= 0

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


def init():
    global clocks,counters, logs, submodules, me, rw, nav, gps, rb, w3, fsm, rs, erb, rgb, gs, byzantine_style, log_folder, estimate, target
    robotID = str(int(robot.variables.get_id()[2:])+1)
    robot.variables.set_attribute("id", str(robotID))
    robot.variables.set_attribute("byzantine_style", str(0))
    robot.variables.set_attribute("consensus_reached",str("false"))
    robot.variables.set_attribute("response", "")
    robot.variables.set_attribute("aggregated_content", "")

    # /* Initialize Console Logging*/
    #######################################################################
    log_folder = experimentFolder + '/new_log4_24rob_0byz/' + robotID + '/'

    # Monitor logs (recorded to file)
    name =  'monitor.log'
    os.makedirs(os.path.dirname(log_folder+name), exist_ok=True) 
    logging.basicConfig(filename=log_folder+name, filemode='w+', format='[{} %(levelname)s %(name)s] %(message)s'.format(robotID))
   
    robot.log = logging.getLogger()
    robot.log.setLevel(0)

    # /* Initialize submodules */
    #######################################################################


    # /* Init E-RANDB __listening process and transmit function
    robot.log.info('Initialising RandB board...')
    erb = ERANDB(robot, cp['erbDist'] , cp['erbtFreq'])

    #/* Init Resource-Sensors */
    robot.log.info('Initialising resource sensor...')
    rs = ResourceVirtualSensor(robot)
    
    # /* Init Random-Walk, __walking process */
    robot.log.info('Initialising random-walk...')


    if int(lp['environ']['USEGENERATEDMOVEMENT']) == 1:    
        from controllers.movement_generated import CustomMovement
        rw = CustomMovement(robot, cp['scout_speed'])
    else:
        rw = RandomWalk(robot, cp['scout_speed'])
    

    # # /* Init Navigation, __navigate process */
    # robot.log.info('Initialising navigation...')
    nav = Navigate(robot, cp['scout_speed'])
    
    # # /* Init GPS sensor */
    robot.log.info('Initialising gps...')
    gps = GPS(robot)

    # /* Init LEDs */
    rgb = RGBLEDs(robot)

    # /* Init Finite-State-Machine */
    fsm = FiniteStateMachine(robot, start = States.RANDOMWALK)

    # /* Init Ground sensor */
    robot.log.info('Initialising Ground sensor...')
    gs = GroundSensor(robot)
    
    # List of submodules --> iterate .start() to start all
    submodules = [erb,gs]

    # Initialize output directory
    output_base = os.path.join('controllers', 'outputs')
    llm_output = os.path.join(output_base, str(myround), str(robotID) + '.txt')
    if os.path.exists(output_base):
        shutil.rmtree(output_base)

    # Initialize prompt directory
    prompts_base = os.path.join('controllers', 'prompts')
    if os.path.exists(prompts_base):
        shutil.rmtree(prompts_base)        
    os.makedirs(prompts_base, exist_ok=True)

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

# Extract intent for human-swarm interaction
def extract_info(response_for_human):
    # Extract the activity after "ACTIVITY:"
    activity_match = re.search(r'ACTIVITY:\s*([A-Z\s]+)\n', response_for_human)
    activity = activity_match.group(1).strip() if activity_match else None

    # Extract the coordinates after "TARGET:"
    target_match = re.search(r'TARGET:\s*\(([\d\.\-]+),\s*([\d\.\-]+)\)', response_for_human)
    if target_match:
        coordinates = (float(target_match.group(1)), float(target_match.group(2)))
    else:
        coordinates = None

    return activity, coordinates



def controlstep():
    global counter, last, pos, clocks, counters, startFlag, startTime, odo2, checkt, byzantine, byzantine_style, log_folder, target
    global estimate, totalWhite, totalBlack, robotID
    global myround, rw

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

    if byzantine_style == 1:
        fsm.setState(States.BROKENWHEELS)

    for module in [erb, rs, gs]:
        module.step()

    # State machine for movement
    if fsm.query(States.IDLE):
        nav.stop()

    elif fsm.query(States.RANDOMWALK):
        rw.step()

    elif fsm.query(States.BROKENWHEELS):
        rw.stop()

    elif fsm.query(States.NAVIGATE):
        # Navigate to the target
        
        #print("distance", nav.get_distance_to(target))
        if nav.get_distance_to(target) < 0.2:           
            nav.avoid(move = True)
            fsm.setState(States.IDLE)

        else:
            nav.navigate_with_obstacle_avoidance(target)

            
    newValues = gs.getNew()
    current_position = gps.getPosition()

    # Read ground sensor one time per second
    sensor_rate = 10


    #if ((counter + 1) % 1000) == 0: 
    #    print(estimate)

    if ((counter + 1) % sensor_rate) == 0: 
        estimate.append((round(newValues[1],2), round(current_position[0], 2), round(current_position[1], 2)))


    # Robot-to-robot interaction
    discussion_period = float(lp['environ']['DISCUSSIONPERIOD'])
    if ((counter + 1) % discussion_period) == 0: 

        myround += 1

        # Read previous outputs (if it is not the first discussion round)
        
        aggregated_content = ""

        if myround > 1:
            for m in range(myround - 1):
                for i in range(1, int(lp['environ']['NUMROBOTS']) + 1): 
                    filepath = 'controllers/outputs/' + str(myround - 1) + "/" + str(i) + '.txt'
                    with open(filepath, 'r') as file:
                        llm_output = file.read()

                        # aggregated_content += f"Robot {i}\n\n{llm_output}\n\n"
                        aggregated_content += "### Robot " + str(i) + "###\n\n" + llm_output + "\n\n ### End information Robot " + str(i) + '\n\n'
                        #aggregated_content += ""

        robot.variables.set_attribute("aggregated_content", aggregated_content)


        # Convert 1.0 to "crops", 0.0 to "weeds", and anything else to "injured person"
        if byzantine_style == 0 or byzantine_style == 1:
            converted_estimate = [
                (
                    "crops" if entry[0] == 0.8 else
                    "crops" if entry[0] == 0.81 else
                    "weeds" if entry[0] == 0.6 else
                    "injured person" if entry[0] == 0.37 else
                    "injured person" if entry[0] == 0.21 else
                    "unknown",
                    entry[1],
                    entry[2]
                )
            for entry in estimate]
        elif byzantine_style == 2: 
            converted_estimate = [
                ("weeds", entry[1], entry[2])
                for entry in estimate]


        # print(estimate)
        # print(converted_estimate)

        # Define the placeholders and their replacements
        placeholders = {
            '{robotID}': str(robotID),
            '{estimate}': ', '.join(str(x) for x in converted_estimate),
            '{results}': aggregated_content,
            '{round}': str(myround)}

        #print(totalWhite, totalBlack, converted_estimate)

        template_base = os.path.join('controllers', 'prompt_templates')
        my_system_prompt = os.path.join(template_base, lp['environ']['SYSTEMMESSAGETEMPLATE'])

        user_message_template = os.path.join(template_base, lp['environ']['USERMESSAGETEMPLATE'])

        # Read the file contents
        with open(user_message_template, 'r') as file:
            msg = file.read()
        
        # Replace the placeholders in the prompt template
        for placeholder, replacement in placeholders.items():
            msg = msg.replace(placeholder, replacement)

        # Create the prompt for this robot
        my_user_prompt = os.path.join('controllers', 'prompts', str(robotID) + '_prompt.txt')
        with open(my_user_prompt, 'w') as file:
            os.makedirs(os.path.dirname(my_user_prompt), exist_ok=True)
            file.write(msg)

        print("Robot " + str(robotID) + " currently interacting with LLM") 

        # Send the command to the LLM, retrieve the response, and store it
        my_command = "python3 controllers/openai-api.py " + my_system_prompt + " " + my_user_prompt     # TODO: Use the complete file path here instead of numbers
        response = os.popen(my_command).read()
        robot.variables.set_attribute("response", response)

        
        print_response =  int(lp['environ']['PRINTLLMRESPONSE'])
        if print_response == 1:
            print("LLM RESPONSE OF ROBOT " + str(robotID))
            print(response)
            print("END LLM RESPONSE OF ROBOT " + str(robotID) + "\n\n")


        # Save the LLM response of this robot in a file
        filepath = os.path.join("controllers", "outputs", str(myround) + "/" + robotID + ".txt") 
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'a') as file:
            file.write(response)

        estimate = []


    # Human-swarm interaction
    human_interaction_period = float(lp['environ']['HUMANINTERACTIONPERIOD'])
    #if ((counter + 1) % human_interaction_period) == 0:# and (str(robotID) == "1"):
    if counter == human_interaction_period:# and (str(robotID) == "1"):

        human_system_prompt = os.path.join('controllers', 'prompt_templates', lp['environ']['SYSTEMHUMAN'])
        human_user_prompt_template = os.path.join('controllers', 'prompt_templates', lp['environ']['USERHUMAN'])

        
        # Read the system message for robot-robot interaction (in order to inform the human what the robots' task is)
        with open(os.path.join('controllers', 'prompt_templates', lp['environ']['SYSTEMMESSAGETEMPLATE']), 'r') as file:
            task = file.read()            


        aggregated_content = ""

        # Read the results of the previous robot interactions
        for m in range(myround):
            for i in range(1, int(lp['environ']['NUMROBOTS']) + 1): 
                filepath = 'controllers/outputs/' + str(myround) + "/" + str(i) + '.txt'
                with open(filepath, 'r') as file:
                    llm_output = file.read()

                    aggregated_content += "### Robot " + str(i) + "###\n\n" + llm_output + "\n\n ### End information Robot " + str(i) + '\n\n'


        # Define the placeholders and their replacements
        placeholders = {
            '{robotID}': str(robotID),
            '{results}': aggregated_content,
            '{round}': str(myround),
            '{task}': task
            }


        # Read the file contents
        with open(human_user_prompt_template, 'r') as file:
            msg = file.read()
        


        # Replace the placeholders in the prompt template
        for placeholder, replacement in placeholders.items():
            msg = msg.replace(placeholder, replacement)

        # Create the prompt for this robot
        human_user_prompt = os.path.join('controllers', 'prompts',  str(robotID) + '_prompt_for_human.txt')
        with open(human_user_prompt, 'w') as file:
            os.makedirs(os.path.dirname(human_user_prompt), exist_ok=True)
            file.write(msg)


        if str(robotID) == "1":
            print("\nThe human sends the following message:\n")
            with open(human_user_prompt, 'r') as file:
                mymsg = file.read()
                print(mymsg)
                print("\n")

        # Send the command to the LLM and retrieve the response
        mycommand = "python3 controllers/openai-api.py " + human_system_prompt + " " + human_user_prompt
        response_for_human = os.popen(mycommand).read()
        
        
        print("Robot " + str(robotID))
        print(response_for_human)

        # Save the LLM response of this robot in a file
        filepath = os.path.join("controllers","outputs", str(myround) + "/" + robotID + "for_human.txt")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as file:
            file.write(response_for_human)


        # Check if the human prompt contained an INSTRUCTION
        activity, target = extract_info(response_for_human)

        #print(activity)
        #print(target)

        if activity == "TARGETED NAVIGATION":
            #print("STOPPING RANDOM WALK STARTING TARGETED NAVIGATION")
            rw.stop()
            fsm.setState(States.NAVIGATE)


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
