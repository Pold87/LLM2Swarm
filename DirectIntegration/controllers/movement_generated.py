#!/usr/bin/env python3
import math
from aux import Vector2D

class CustomMovement:
    def __init__(self, robot, MAX_SPEED):
        self.robot = robot
        self.MAX_SPEED = MAX_SPEED
        self.timestep = 0
        self.L = 0.053  # Distance between wheels
        self.Kp = 50  # Proportional gain for angular velocity
        self.thresh = math.radians(70)  # Threshold angle for moving
        self.arena_center = Vector2D(0, 0)  # Assuming the center of the arena is at (0, 0)

    def step(self):
        self.timestep += 1
        if self.timestep < 150:
            self.aggregate()
        else:
            self.disperse()

    def aggregate(self):
        self.move_towards(self.arena_center)

    def disperse(self):
        current_position = Vector2D(self.robot.position.get_position()[0:2])
        direction_away = (current_position - self.arena_center).normalize()
        target_position = current_position + direction_away
        self.move_towards(target_position)

    def move_towards(self, target):
        position = Vector2D(self.robot.position.get_position()[0:2])
        orientation = self.robot.position.get_orientation()
        vec_target = (target - position).rotate(-orientation)
        T = vec_target.normalize()

        dotProduct = 0
        if T.angle > self.thresh or T.angle < -self.thresh:
            dotProduct = 0
        else:
            dotProduct = Vector2D(1, 0).dot(T)

        angularVelocity = self.Kp * T.angle

        right = dotProduct * self.MAX_SPEED / 2 - angularVelocity * self.L
        left = dotProduct * self.MAX_SPEED / 2 + angularVelocity * self.L

        self.robot.epuck_wheels.set_speed(right, left)