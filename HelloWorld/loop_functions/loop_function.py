#!/usr/bin/env python3

import os
import sys
import random
import logging, time, json
import libpy_loop_function_interface
from hexbytes import HexBytes

from controllers.aux import Vector2D, Logger, Timer, Accumulator, mydict, identifiersExtract, Counter
from controllers.groundsensor import Resource
from loop_functions.loop_params import params as lp

from controllers.control_params import params as cp
#from loop_params import params as lp
#from loop_helpers import *

# Initialize loop function interface
loop_function_interface = libpy_loop_function_interface.CPyLoopFunction()

# Global variables
global startFlag, stopFlag, startTime
startFlag = False
stopFlag = False
startTime = 0

# Initialize timers/accumulators/logs
global clocks, accums, logs, other,addspacebetweenrobots
addspacebetweenrobots = 0
clocks, accums, logs, other = dict(), dict(), dict(), dict()
other['countsim'] = Counter()
# Function definitions
def init():
    global addspacebetweenrobots
    for robot in allrobots:
        addspacebetweenrobots +=0.1 #INITIALIZE robots IN DIFF PLACES-TO BE FIXED
        robot.id = int(robot.variables.get_attribute("id"))
        #print("IN INIT FUNCTION",robot.id)
        #SPECIFY THE ROBOT IDS TO BE OUTSIDE THE ARENA AND INACTIVE
        #if(robot.id == 1 or robot.id ==2 or robot.id == 3 or robot.id == 4 or robot.id ==5 or robot.id ==6):
        #if(robot.id == 1 or robot.id ==2):
         #   loop_function_interface.AddRobotArena(0.8,0.93,0)
        #    loop_function_interface.AddRobotArena(0.9-addspacebetweenrobots,0.93, int(robot.id)-1)
    #"""
    byzantines = random.sample(allrobots, k=int(lp['environ']['NUMBYZANTINE']))
    for robot in byzantines:
        robot.variables.set_attribute("byzantine_style", lp['environ']['BYZANTINESWARMSTYLE'])
        print("Making robot", robot.variables.get_attribute("id"), "Byzantine.")
        robot.variables.set_attribute("isByz","True")
    #"""

def pre_step():
    global startFlag, startTime
    if not startFlag:
        startTime = 0
    """
    if other['countsim'].count == 0:
        try:
            loop_function_interface.AddRobotArena(0.8, 0.93, 0)
            loop_function_interface.AddRobotArena(0.9, 0.93, 1)
            loop_function_interface.AddRobotArena(0.7, 0.93, 2)
            loop_function_interface.AddRobotArena(0.6, 0.93, 3)


        except Exception as e:
            print(f"An error occurred: {e}")
    """
def post_step():
    global startFlag, clocks, accums
    other['countsim'].step()
    """
    if other['countsim'].count == 150:
        try:
            loop_function_interface.AddRobotArena(0.5, 0.0, 0)
            loop_function_interface.AddRobotArena(0.5, 0.1, 1)
            loop_function_interface.AddRobotArena(0.5, 0.2, 2)
            loop_function_interface.AddRobotArena(0.5, 0.3, 3)

        except Exception as e:
            print(f"An error occurred: {e}")
    """

def is_experiment_finished():
    pass

def reset():
    pass

def destroy():
    pass

def post_experiment():
    print("Finished from Python!")
