#!/usr/bin/env python3

# Import Packages
import os
import sys
import math

# Add necessary paths
experimentFolder = os.environ['EXPERIMENTFOLDER']
sys.path += [os.environ['MAINFOLDER'],
             os.environ['EXPERIMENTFOLDER'] + '/controllers',
             os.environ['EXPERIMENTFOLDER']]

# Import the required modules
from controllers.movement import CustomMovement

# Global Variables
global robot

# Controller class for custom movement
class CustomMovement:
    def __init__(self, robot, speed):
        self.robot = robot
        self.speed = speed
        self.counter = 0  # Keep track of timesteps

    def start(self):
        # Initialize movement
        self.move()

    def move(self):
        if self.counter < 100:
            # Spin the robot
            self.spin()
        elif self.counter < 125:
            # Pause
            self.pause()
        else:
            # Reset counter to loop the behavior
            self.counter = 0

        self.counter += 1

    def spin(self):
        # Setting wheel velocities to spin the robot
        self.robot.wheels.set_velocity([self.speed, -self.speed])

    def pause(self):
        # Pausing the robot
        self.robot.wheels.set_velocity([0, 0])

def init():
    global custom_movement
    robotID = str(int(robot.variables.get_id()[2:]) + 1)

    # Initialize Custom Movement
    custom_movement = CustomMovement(robot, speed=10)

def controlstep():
    global custom_movement
    # Perform the custom movement step
    custom_movement.move()

def reset():
    pass

def destroy():
    pass