#!/usr/bin/env python3
import random, math
import os

params = dict()
params['scout_speed']    = 18
params['recruit_speed']  = 18
params['buy_duration']   = 30


params['gsFreq']     = 20
params['erbtFreq']   = 10
params['erbDist']    = 175

# Maximum quantity of resource a robot can transport
params['max_Q']       = 10

params['firm'] = dict()
params['firm']['entry_K']     = 5