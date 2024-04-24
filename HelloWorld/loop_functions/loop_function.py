#!/usr/bin/env python3

# /* Import Packages */
#######################################################################
import random, math
import time, sys, os, json
import logging
import libpy_loop_function_interface
from hexbytes import HexBytes

sys.path += [os.environ['EXPERIMENTFOLDER']+'/controllers', \
             os.environ['EXPERIMENTFOLDER']+'/loop_functions', \
             os.environ['EXPERIMENTFOLDER']]

from controllers.aux import Vector2D, Logger, Timer, Accumulator, mydict, identifiersExtract, Counter
from controllers.groundsensor import Resource

from controllers.control_params import params as cp
from loop_params import params as lp
from loop_helpers import *

random.seed(lp['generic']['seed'])

log_folder = lp['environ']['EXPERIMENTFOLDER'] + '/logs/0/'
os.makedirs(os.path.dirname(log_folder), exist_ok=True)   
loop_function = libpy_loop_function_interface.CPyLoopFunction()

# /* Global Variables */
#######################################################################

# Other inits
global startFlag, stopFlag, startTime
startFlag = False
stopFlag = False
startTime = 0

# Get ticks per second from experimentconfig.sh file
TPS = int(lp['environ']['TPS'])

# Initialize timers/accumulators/logs:
global clocks, accums, logs, other
clocks, accums, logs, other = dict(), dict(), dict(), dict()

clocks['simlog'] = Timer(10*TPS)
accums['collection'] = [Accumulator() for i in range(lp['generic']['num_robots']+1)]
other['countsim'] = Counter()
clocks['block']      = Timer(15*TPS)
clocks['forage']     = dict()
global allrobots


def init():

    # Init robot parameters
    addspacebetweenrobots = 0
    for robot in allrobots:
        addspacebetweenrobots +=0.1 #INITIALIZE robots IN DIFF PLACES-TO BE FIXED
        robot.id = int(robot.variables.get_attribute("id"))
        #print("IN INIT FUNCTION",robot.id)
        #SPECIFY THE ROBOT IDS TO BE OUTSIDE THE ARENA AND INACTIVE
        if(robot.id == 1 or robot.id ==2 or robot.id == 3 or robot.id == 4 or robot.id ==5 or robot.id ==6):
            loop_function.AddRobotArena(0.9-addspacebetweenrobots,0.93, robot.id-1)

        other['countsim'].reset()
        #print(robot.position.get_position())

def pre_step():
    global startFlag, startTime

    # Tasks to perform on the first time step
    if not startFlag:
        startTime = 0

def post_step():
    #print("py prestep")
    global startFlag, clocks, accums
    other['countsim'].step()
    if(other['countsim'].count== 50):
        #MOVE ROBOTS BACK TO ARENA AT CERTAIN TIMESTEP
        loop_function.AddRobotArena(0.5,0.0, 0)
        loop_function.AddRobotArena(0.5,0.1, 1)
        loop_function.AddRobotArena(0.5,0.2, 2)
        loop_function.AddRobotArena(0.5,0.3, 3)
        loop_function.AddRobotArena(0.5,0.4, 4)
        loop_function.AddRobotArena(0.5,0.5, 5)
        loop_function.AddRobotArena(0.5,0.6, 6)
        #try:

        #except Exception as e:
            #print("Error:", e)

        #new_rob()
        #loop_function = libpy_loop_function_interface.CPyLoopFunction()
        #loop_function.add_epuck_entity((0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 1.0))
    
    #print(other['countsim'].count)
    #for robot in allrobots:
        #robot.id = int(robot.variables.get_attribute("id"))
        #print(robot.id)
    #if not startFlag:
        #startFlag = False

# Function to add an e-puck entity to the simulation


    
def is_experiment_finished():
    pass

def reset():
    pass

#def add_robot():
#    print("adding new rob check")

def destroy():
    pass

def post_experiment():
    print("Finished from Python!")
    
def add_robot():
    print("Moving bots")



