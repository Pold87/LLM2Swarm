#!/usr/bin/env python3
import random, math
import time
import logging

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

    def __sub__(self, other):
        """Vector subtraction."""
        return Vector2D(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        """Vector addition."""
        return Vector2D(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        """Multiplication of a vector by a scalar."""

        if isinstance(scalar, int) or isinstance(scalar, float):
            return Vector2D(self.x*scalar, self.y*scalar)
        raise NotImplementedError('Can only multiply Vector2D by a scalar')

    def __truediv__(self, scalar):
        """True division of the vector by a scalar."""
        return Vector2D(self.x / scalar, self.y / scalar)

    def __abs__(self):
        """Absolute value (magnitude) of the vector."""
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self):
        """Normalized vector"""
        if self.x == 0 and self.y == 0:
            return self
        else:
            return Vector2D(self.x/abs(self), self.y/abs(self))

    def distance_to(self, other):
        """The distance between vectors self and other."""
        return abs(self - other)

class FlockingController(object):
    """A controller to make robots flock together using ARGoS simulator."""

    def __init__(self, robot, max_speed):
        self.robot = robot
        self.max_speed = max_speed

        # Flocking parameters
        self.flock_range = 0.2  # Communication range for flocking
        self.cohesion_strength = 1.0  # Strength of the cohesion force
        self.separation_strength = 1.5  # Strength of the separation force
        self.alignment_strength = 1.0  # Strength of the alignment force

    def step(self):
        """This method runs in the background until program is closed."""

        left_speed, right_speed = self.compute_flocking()

        left_speed, right_speed = self.saturate_speeds(left_speed, right_speed)

        self.robot.epuck_wheels.set_speed(left_speed, right_speed)

    def compute_flocking(self):
        cohesion_force = Vector2D()
        separation_force = Vector2D()
        alignment_force = Vector2D()

        neighbors = self.robot.epuck_proximity.get_readings()

        neighbor_count = 0

        for neighbor in neighbors:
            angle = neighbor.angle
            distance = neighbor.value
            
            if distance < self.flock_range:
                neighbor_count += 1
                neighbor_pos = Vector2D(math.cos(angle) * distance, math.sin(angle) * distance)

                cohesion_force += neighbor_pos

                if distance < 0.05:
                    separation_force -= neighbor_pos / (distance + 1e-5)

                alignment_force += Vector2D(math.cos(angle), math.sin(angle))

        if neighbor_count > 0:
            cohesion_force /= neighbor_count
            alignment_force = (alignment_force / neighbor_count).normalize()

            resultant_force = self.cohesion_strength * cohesion_force + \
                              self.separation_strength * separation_force + \
                              self.alignment_strength * alignment_force

            velocity = abs(resultant_force)
            angle = math.atan2(resultant_force.y, resultant_force.x)

            left_speed = velocity + angle
            right_speed = velocity - angle
        else:
            left_speed = self.max_speed / 2
            right_speed = self.max_speed / 2

        return left_speed, right_speed

    def saturate_speeds(self, left_speed, right_speed):
        if left_speed > self.max_speed:
            left_speed = self.max_speed
        elif left_speed < -self.max_speed:
            left_speed = -self.max_speed

        if right_speed > self.max_speed:
            right_speed = self.max_speed
        elif right_speed < -self.max_speed:
            right_speed = -self.max_speed

        return left_speed, right_speed

    def start(self):
        pass

    def stop(self):
        pass