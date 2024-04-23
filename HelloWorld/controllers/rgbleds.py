#!/usr/bin/env python3
import time
from controllers.aux import Timer

class RGBLEDs(object):
    """ Interact with the 3 RGB leds on the top of the pi-puck
    """
    def __init__(self, robot):
        """ Constructor
        """
        self.robot = robot

        self.led1 = 0x00
        self.led2 = 0x01
        self.led3 = 0x02
        self.all = [self.led1, self.led2, self.led3]

        self.red = 'red'
        self.green = 'green'
        self.blue = 'blue'
        self.off = 'black'
        self.white = 'white'

        self.presets = {
                        0: ['black', 'black', 'black'],
                        1: ['red', 'black', 'black'],
                        2: ['red', 'black', 'red']
                        }

        self.frozen = False
        self.timer  = time.time()

    def _from_string(self, color_string):
        return getattr(self, color_string, None)		

    def setAll(self, color):
        if isinstance(color, str):
            self.robot.epuck_leds.set_all_colors(color)
        elif hasattr(color, '__iter__'):
            self.robot.epuck_leds.set_all_colors(*color)
        else:
            print('Input must be string or RGB array')

    def flashAll(self, color, delay=1):
        if isinstance(color, str):
            color = self._from_string(color)
    
        if not self.frozen:
            self.setLED(self.all, 3*[color])
            time.sleep(delay)
            self.setLED(self.all, 3*[color])

    def setLED(self, LED, RGB):
        if not self.frozen:
            for i in range(len(LED)):
                self.robot.epuck_leds.set_single_color(LED[i], RGB[i])

    def freeze(self):
        self.frozen = True

    def unfreeze(self):
        self.frozen = False

    def stop(self):
        self.unfreeze()
        self.setLED(self.all, 3* [self.off])