#!/usr/bin/env python3

# /* Import Packages */
#######################################################################
import random, math
import sys, os
import hashlib

sys.path += [os.environ['EXPERIMENTFOLDER']+'/controllers', \
             os.environ['EXPERIMENTFOLDER']+'/loop_functions', \
             os.environ['EXPERIMENTFOLDER']]

from controllers.groundsensor import Resource
from controllers.aux import Vector2D

from controllers.control_params import params as cp
from loop_params import params as lp


global robot, environment


def draw_resources_on_robots():
        pass


def init():
	pass

def draw_in_world():
	pass

def draw_in_robot():
        pass
        
def destroy():
	print('Closing the QT window')
