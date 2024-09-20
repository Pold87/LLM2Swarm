#!/usr/bin/env python3
import random, math
import time
import logging
from aux import Vector2D

class Vector2D:
    """A two-dimensional vector with Cartesian coordinates."""

    def __init__(self, x = 0, y = 0, polar = False, degrees = False):

            self.x = x
            self.y = y

            if isinstance(x, (Vector2D, list, tuple)) and not y: 
                self.x = x[0]
                self.y = x[1]
            
            if degrees:
                y = math.radians(y)

            if polar:
                self.x = x * math.cos(y)
                self.y = x * math.sin(y)

            self.length = self.__abs__()
            self.angle = math.atan2(self.y, self.x)

    def __str__(self):
        """Human-readable string representation of the vector."""
        return '{:g}i + {:g}j'.format(self.x, self.y)

    def __repr__(self):
        """Unambiguous string representation of the vector."""
        return repr((self.x, self.y))

    def dot(self, other):
        """The scalar (dot) product of self and other. Both must be vectors."""

        if not isinstance(other, Vector2D):
            raise TypeError('Can only take dot product of two Vector2D objects')
        return self.x * other.x + self.y * other.y
    # Alias the __matmul__ method to dot so we can use a @ b as well as a.dot(b).
    __matmul__ = dot

    def cross(self, other):
        """The vector (cross) product of self and other. Both must be vectors."""

        if not isinstance(other, Vector2D):
            raise TypeError('Can only take cross product of two Vector2D objects')
        return abs(self) * abs(other) * math.sin(self-other)
    # Alias the __matmul__ method to dot so we can use a @ b as well as a.dot(b).
    __matmul__ = cross

    def __sub__(self, other):
        """Vector subtraction."""
        return Vector2D(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        """Vector addition."""
        return Vector2D(self.x + other.x, self.y + other.y)

    def __radd__(self, other):
        """Recursive vector addition."""
        return Vector2D(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        """Multiplication of a vector by a scalar."""

        if isinstance(scalar, int) or isinstance(scalar, float):
            return Vector2D(self.x*scalar, self.y*scalar)
        raise NotImplementedError('Can only multiply Vector2D by a scalar')

    def __rmul__(self, scalar):
        """Reflected multiplication so vector * scalar also works."""
        return self.__mul__(scalar)

    def __neg__(self):
        """Negation of the vector (invert through origin.)"""
        return Vector2D(-self.x, -self.y)

    def __truediv__(self, scalar):
        """True division of the vector by a scalar."""
        return Vector2D(self.x / scalar, self.y / scalar)

    def __mod__(self, scalar):
        """One way to implement modulus operation: for each component."""
        return Vector2D(self.x % scalar, self.y % scalar)

    def __abs__(self):
        """Absolute value (magnitude) of the vector."""
        return math.sqrt(self.x**2 + self.y**2)

    def __round__(self, decimals):
        """Round the vector2D x and y"""
        return Vector2D(round(self.x, decimals), round(self.y, decimals))

    def __iter__(self):
        """Return the iterable object"""
        for i in [self.x, self.y]:
            yield i

    def __getitem__(self, index):
        """Return the iterable object"""
        if index == 0 or index == 'x':
            return self.x
        elif index == 1 or index == 'y':
            return self.y
        raise NotImplementedError('Vector2D is two-dimensional array (x,y)')


    def rotate(self, angle, degrees = False):
        if degrees:
            angle = math.radians(angle)
            
        return Vector2D(self.length, self.angle + angle, polar = True)

    def normalize(self):
        """Normalized vector"""
        if self.x == 0 and self.y == 0:
            return self
        else:
            return Vector2D(self.x/abs(self), self.y/abs(self))

    def distance_to(self, other):
        """The distance between vectors self and other."""
        return abs(self - other)

    def to_polar(self):
        """Return the vector's components in polar coordinates."""
        return self.length, self.angle

class RandomWalk(object):
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

            # Avoid Obstacles
            left, right = self.avoid_argos3_example(left, right)

            # Saturate wheel actuators
            left, right = self.saturate(left, right)

            # Set wheel speeds
            self.robot.epuck_wheels.set_speed(right, left)

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
            angle = reading.angle  # Correctly access the angle
            distance = reading.value  # Correctly access the distance
            # Check if the other robot is within flocking range
            if distance < self.flock_range:
                vec = Vector2D(
                    math.cos(angle) * distance, math.sin(angle) * distance)
                neighbors.append(vec)

                # Compute cohesion force (move towards the average position)
                cohesion_force += vec

                # Compute separation force (move away from very close neighbors)
                if distance < 0.05:  # Consider neighbors that are very close
                    separation_force -= vec / (distance + 1e-5)

                # Compute alignment force (align velocity with neighbors)
                alignment_force += Vector2D(
                    math.cos(angle), math.sin(angle))
                strength += 1

        if strength > 0:
            cohesion_force /= strength
            alignment_force /= strength

            # Combine all forces
            resultant_force = self.alpha * cohesion_force + \
                self.beta * separation_force + self.gamma * alignment_force

            # Convert the resultant force to wheel speeds
            velocity = math.sqrt(resultant_force.x ** 2 + resultant_force.y ** 2)
            angle = math.atan2(resultant_force.y, resultant_force.x)
            left_wheel = velocity + self.Kp * angle
            right_wheel = velocity - self.Kp * angle

            return left_wheel, right_wheel

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

