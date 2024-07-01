#!/usr/bin/env python3
import math, random, time
import logging
import json

from aux import Vector2D

class GroundSensor(object):
    """ Set up a ground-sensor data acquisition loop on a background thread
    The __sensing() method will be started and it will run in the background
    until the application exits.
    """
    def __init__(self, robot, freq = 20):
        """ Constructor
        :type freq: str
        :param freq: frequency of measurements in Hz (tip: 20Hz)
        """
        self.freq = freq
        self.groundValues = [0 for x in range(3)]
        self.groundCumsum = [0 for x in range(3)]
        self.count = 0
        self.robot = robot

        logging.basicConfig(format='[%(levelname)s %(name)s %(relativeCreated)d] %(message)s')
        logger = logging.getLogger(__name__)

    def step(self):
        """ This method runs in the background until program is closed 
        """  

        # Initialize variables
        self.groundValues = self.robot.epuck_ground.get_readings()

        # Compute cumulative sum
        self.groundCumsum[0] += self.groundValues[0] 
        self.groundCumsum[1] += self.groundValues[1]
        self.groundCumsum[2] += self.groundValues[2]
        self.count += 1


    def getAvg(self):
        """ This method returns the average ground value since last call """

        # Compute average
        try:
            groundAverage =  [round(x/self.count) for x in self.groundCumsum]
        except:
            groundAverage = None

        self.count = 0
        self.groundCumsum = [0 for x in range(3)]
        return groundAverage

    def getNew(self):
        """ This method returns the instant ground value """

        return self.groundValues;
        
    def start(self):
        pass

    def stop(self):
        pass

class Resource(object):
    """ Establish the resource class 
    """
    def __init__(self, resource_js):
        # Required resource attrs: x, y, radius

        if isinstance(resource_js, dict):
            resource_dict = resource_js
        else:
            resource_dict = json.loads(resource_js.replace("\'", "\""))

        # Read the default resource attributes
        for attr in resource_dict:
            setattr(self, attr, resource_dict[attr])

        # Fix the number of decimals
        self.x = round(self.x, 2)
        self.y = round(self.y, 2)

        # Introduce the measurement error
        r = self.radius * math.sqrt(random.random()) * 0
        theta = 2 * math.pi * random.random()
        self._xr = self.x + r * math.cos(theta)
        self._yr = self.y + r * math.sin(theta)
        
        self._pr = (self._xr, self._yr)
        self._p  = (self.x, self.y)
        self._pv  = Vector2D(self.x, self.y)

        # Introduce the timestamp
        self._timeStamp = time.time()
        self._isSold = False

    @property
    def _json(self):
        public_vars = { k:v for k,v in vars(self).items() if not k.startswith('_')}
        return str(public_vars).replace("\'", "\"")

    @property
    def _desc(self):
        return '{%s, %s, %s, %s}' % (self.x, self.y, self.quality, self.quantity)

    @property
    def _calldata(self):
        return (self.x, 
                self.y,  
                int(max(0,self.quantity)),
                int(self.utility), 
                str(self.quality), 
                str(self._json))

class ResourceVirtualSensor(object):
    """ Set up a ground-sensor data acquisition loop on a background thread
    The __sensing() method will be started and it will run in the background
    until the application exits.
    """
    def __init__(self, robot, freq = 100):
        """ Constructor
        :type freq: str
        :param freq: frequency of measurements in Hz (tip: 20Hz)
        """
        self.robot = robot
        self.freq = freq
        self.last = time.time()
        self.resource = None

    def step(self):

        # Read frequency @ self.freq (Hz).
        if time.time() - self.last > (1/self.freq):
            self.last = time.time()

            resource = self.robot.variables.get_attribute("newResource")
            if resource:
                self.resource = resource
            else:
                self.resource = None

    def getNew(self):
        """ This method returns the instant ground value """
        if self.resource:
            return Resource(self.resource)

                     
    # def getNew(self):
    #     """ This method returns the instant ground value """
    #     temp = None
    #     if self.resource:
    #         temp = Resource(self.resource)
    #     self.resource = None
    #     return temp    

    def start(self):
        pass

    def stop(self):
        pass