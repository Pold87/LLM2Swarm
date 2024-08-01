#!/usr/bin/env python3
import random, math
import time
import logging
from aux import Vector2D


class RandomWalk(object):
    """ Set up a Random-Walk loop on a background thread
    The __walking() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, robot, MAX_SPEED):
        """ Constructor
        :type range: int
        :param enode: Random-Walk speed (tip: 500)
        """
        self.__stop = 1
        self.__walk = True
        self._id = str(int(robot.variables.get_id()[2:])+1)
        self.__distance_to_target = None
        self.__distance_traveled = 0

        # General Parameters
        self.robot = robot
        self.MAX_SPEED = MAX_SPEED                          

        # Random walk parameters
        self.remaining_walk_time = 3
        self.my_lambda = 10              # Parameter for straight movement
        self.turn = 8
        self.possible_directions = ["straight", "cw", "ccw"]
        self.actual_direction = "straight"

        # Navigation parameters
        self.L = 0.053                    # Distance between wheels
        self.R = 0.0205                   # Wheel radius
        self.Kp = 5                       # Proportional gain
        self.thresh = math.radians(70)    # Wait before moving

        # Obstacle avoidance parameters
        self.thresh_ir = 0
        self.weights  = 50 * [-10, -10, 0, 0, 0, 0, 10, 10]

        # Vectorial obstacle avoidance parameters
        self.vec_avoid = []
        self.__old_time = time.time()
        self.__old_vec = 0
        self.__accumulator_I = 0
        

    def step(self):
        """ This method runs in the background until program is closed """

        if self.__walk:

            # Levy random-Walk
            left, right = self.random()

            # Avoid Obstacles
            left, right = self.avoid_argos3_example(left, right)

            # Saturate wheel actuators
            left, right = self.saturate(left, right)

            # Set wheel speeds
            self.robot.epuck_wheels.set_speed(right, left)

            # No rays for plotting
            self.robot.variables.set_attribute("rays", "")

    def random(self): 

        # Decide direction to take
        if (self.remaining_walk_time == 0):
            if self.actual_direction == "straight":
                self.actual_direction = random.choice(self.possible_directions)
                self.remaining_walk_time = random.randint(0, self.turn)
            else:
                self.actual_direction = "straight"
                self.remaining_walk_time = math.ceil(random.expovariate(1/(self.my_lambda * 4)))
        else:
            self.remaining_walk_time -= 1

        # Return wheel speeds
        speed = self.MAX_SPEED/2

        if (self.actual_direction == "straight"):
            return speed, speed

        elif (self.actual_direction == "cw"):
            return speed, -speed

        elif (self.actual_direction == "ccw"):
            return -speed, speed


    def avoid(self, left = 0, right = 0, move = False):

        obstacle = avoid_left = avoid_right = 0

        # Obstacle avoidance
        readings = self.robot.epuck_proximity.get_readings()
        self.ir = [reading.value for reading in readings]
                
        # Find Wheel Speed for Obstacle Avoidance
        for i, reading in enumerate(self.ir):
            if reading > self.thresh_ir:
                obstacle = True
                avoid_left  += self.weights[i] * reading
                avoid_right -= self.weights[i] * reading

        if obstacle:
            left  = self.MAX_SPEED/2 + avoid_left
            right = self.MAX_SPEED/2 + avoid_right

        if move:
            self.robot.epuck_wheels.set_speed(right, left)

        return left, right

    def avoid_argos3_example(self, left, right):
        # Obstacle avoidance; translated from C++
        # Source: https://github.com/ilpincy/argos3-examples/blob/master/controllers/epuck_obstacleavoidance/epuck_obstacleavoidance.cpp
        
        readings = self.robot.epuck_proximity.get_readings()
        self.ir = [reading.value for reading in readings]

        fMaxReadVal = self.ir[0]
        unMaxReadIdx = 0

        if(fMaxReadVal < self.ir[1]): 
            fMaxReadVal = self.ir[1]
            unMaxReadIdx = 1

        if(fMaxReadVal < self.ir[7]): 
            fMaxReadVal = self.ir[7]
            unMaxReadIdx = 7

        if(fMaxReadVal < self.ir[6]): 
            fMaxReadVal = self.ir[6]
            unMaxReadIdx = 6

        # Do we have an obstacle in front?
        if(fMaxReadVal > 0):
            # Yes, we do: avoid it 
            if(unMaxReadIdx == 0 or unMaxReadIdx == 1): 
                # The obstacle is on the right, turn left 
                left, right = -self.MAX_SPEED/2, self.MAX_SPEED/2
            else: 
                # The obstacle is on the left, turn right 
                left, right = self.MAX_SPEED/2, -self.MAX_SPEED/2       

        return left, right


    def saturate(self, left, right, style = 1):
        # Saturate Speeds greater than MAX_SPEED

        if style == 1:

            if left > self.MAX_SPEED:
                left = self.MAX_SPEED
            elif left < -self.MAX_SPEED:
                left = -self.MAX_SPEED

            if right > self.MAX_SPEED:
                right = self.MAX_SPEED
            elif right < -self.MAX_SPEED:
                right = -self.MAX_SPEED

        else:

            if abs(left) > self.MAX_SPEED or abs(right) > self.MAX_SPEED:
                left = left/max(abs(left),abs(right))*self.MAX_SPEED
                right = right/max(abs(left),abs(right))*self.MAX_SPEED

        return left, right

    def setWalk(self, state):
        """ This method is called set the random-walk to on without disabling I2C"""
        self.__walk = state

    def setLEDs(self, state):
        """ This method is called set the outer LEDs to an 8-bit state """
        if self.__LEDState != state:
            self.__isLEDset = False
            self.__LEDState = state
        
    def getIr(self):
        """ This method returns the IR readings """
        return self.ir

    def start(self):
        pass

    def stop(self):
        pass

class Flocking(object):
    """ Set up a Flocking loop on a background thread
    The __flocking() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, robot, MAX_SPEED):
        """ Constructor
        :type range: int
        :param enode: Flocking speed (tip: 500)
        """
        self.__stop = 1
        self.__flock = True
        self._id = str(int(robot.variables.get_id()[2:]) + 1)
        self.__distance_to_target = None
        self.__distance_traveled = 0

        # General Parameters
        self.robot = robot
        self.MAX_SPEED = MAX_SPEED

        # Navigation parameters
        self.L = 0.053  # Distance between wheels
        self.R = 0.0205  # Wheel radius
        self.Kp = 5  # Proportional gain
        self.thresh = math.radians(70)  # Wait before moving

        # Obstacle avoidance parameters
        self.thresh_ir = 0
        self.weights = 50 * [-10, -10, 0, 0, 0, 0, 10, 10]

        # Flocking parameters
        self.flock_range = 0.1  # Communication range for flocking
        self.alpha = 10.0  # Attraction force
        self.beta = 5.0  # Repulsion force
        self.gamma = 1.0  # Alignment force

    def step(self):
        """ This method runs in the background until program is closed """

        if self.__flock:
            # Compute Flocking
            left, right = self.flock()

            print(left, right)

            # Avoid Obstacles
            left, right = self.avoid_argos3_example(left, right)

            print(left, right)

            # Saturate wheel actuators
            left, right = self.saturate(left, right)

            print(left, right)

            # Set wheel speeds
            self.robot.epuck_wheels.set_speed(right, left)

            print(left, right)

            # No rays for plotting
            self.robot.variables.set_attribute("rays", "")

    def flock(self):
        # We will use vectors to accumulate the forces for flocking
        cohesion_force = Vector2D(0, 0)
        separation_force = Vector2D(0, 0)
        alignment_force = Vector2D(0, 0)
        strength = 0

        readings = self.robot.epuck_proximity.get_readings()

        neighbors = []  # List to hold the positions of neighbors

        for reading in readings:
            angle = reading.angle.value()
            distance = reading.value
            # Check if the other robot is within flocking range
            if distance < self.flock_range:
                vec = Vector2D(math.cos(angle) * distance, math.sin(angle) * distance)
                neighbors.append(vec)

                # Compute cohesion force (move towards the average position)
                cohesion_force += vec

                # Compute separation force (move away from very close neighbors)
                if distance < 0.05:  # Consider neighbors that are very close
                    separation_force -= vec / (distance + 1e-5)

                # Compute alignment force (align velocity with neighbors)
                alignment_force += Vector2D(math.cos(angle), math.sin(angle))
                strength += 1

        if strength > 0:
            cohesion_force /= strength
            alignment_force /= strength

            # Combine all forces
            resultant_force = self.alpha * cohesion_force + self.beta * separation_force + self.gamma * alignment_force

            # Convert the resultant force to wheel speeds
            velocity = math.sqrt(resultant_force.x ** 2 + resultant_force.y ** 2)
            angle = math.atan2(resultant_force.y, resultant_force.x)
            left_wheel = velocity + self.Kp * angle
            right_wheel = velocity - self.Kp * angle

            return 30 * left_wheel, 30 * right_wheel

        # If no neighbors, move straight ahead
        return self.MAX_SPEED / 2, self.MAX_SPEED / 2

    def avoid_argos3_example(self, left, right):
        # Obstacle avoidance; translated from C++
        # Source: https://github.com/ilpincy/argos3-examples/blob/master/controllers/epuck_obstacleavoidance/epuck_obstacleavoidance.cpp

        readings = self.robot.epuck_proximity.get_readings()
        self.ir = [reading.value for reading in readings]

        fMaxReadVal = self.ir[0]
        unMaxReadIdx = 0

        if fMaxReadVal < self.ir[1]:
            fMaxReadVal = self.ir[1]
            unMaxReadIdx = 1

        if fMaxReadVal < self.ir[7]:
            fMaxReadVal = self.ir[7]
            unMaxReadIdx = 7

        if fMaxReadVal < self.ir[6]:
            fMaxReadVal = self.ir[6]
            unMaxReadIdx = 6

        # Do we have an obstacle in front?
        if fMaxReadVal > 0:
            # Yes, we do: avoid it
            if unMaxReadIdx == 0 or unMaxReadIdx == 1:
                # The obstacle is on the right, turn left
                left, right = -self.MAX_SPEED / 2, self.MAX_SPEED / 2
            else:
                # The obstacle is on the left, turn right
                left, right = self.MAX_SPEED / 2, -self.MAX_SPEED / 2

        return left, right

    def saturate(self, left, right, style=1):
        # Saturate Speeds greater than MAX_SPEED

        if style == 1:

            if left > self.MAX_SPEED:
                left = self.MAX_SPEED
            elif left < -self.MAX_SPEED:
                left = -self.MAX_SPEED

            if right > self.MAX_SPEED:
                right = self.MAX_SPEED
            elif right < -self.MAX_SPEED:
                right = -self.MAX_SPEED

        else:

            if abs(left) > self.MAX_SPEED or abs(right) > self.MAX_SPEED:
                left = left / max(abs(left), abs(right)) * self.MAX_SPEED
                right = right / max(abs(left), abs(right)) * self.MAX_SPEED

        return left, right

    def setFlock(self, state):
        """ This method is called set the flocking behavior to on without disabling I2C"""
        self.__flock = state

    def setLEDs(self, state):
        """ This method is called set the outer LEDs to an 8-bit state """
        if self.__LEDState != state:
            self.__isLEDset = False
            self.__LEDState = state

    def getIr(self):
        """ This method returns the IR readings """
        return self.ir

    def start(self):
        pass

    def stop(self):
        pass
