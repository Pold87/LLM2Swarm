#!/usr/bin/env python3
import math
import random
from aux import Vector2D

class CustomMovement:
    def __init__(self, robot, max_speed):
        self.robot = robot
        self.max_speed = max_speed
        self.aggregation_range = 0.2  # Range within which robots will aggregate
        self.attraction_gain = 10.0  # Gain for attraction force
        self.repulsion_gain = 5.0  # Gain for repulsion force
        self.robot_id = int(robot.variables.get_id()[2:]) + 1

    def step(self):
        # Get the proximity readings
        readings = self.robot.epuck_proximity.get_readings()

        # Initialize the aggregation force
        aggregation_force = Vector2D(0, 0)
        repulsion_force = Vector2D(0, 0)
        neighbor_count = 0

        for reading in readings:
            distance = reading.value
            angle = reading.angle.value()

            # Only consider neighbors within the aggregation range
            if distance < self.aggregation_range:
                neighbor_count += 1
                vec = Vector2D(math.cos(angle) * distance, math.sin(angle) * distance)
                aggregation_force += vec

                if distance < 0.05:  # Repulsion distance threshold
                    repulsion_force -= vec / (distance + 1e-5)

        # Compute the resultant force
        if neighbor_count > 0:
            aggregation_force /= neighbor_count
            resultant_force = self.attraction_gain * aggregation_force + self.repulsion_gain * repulsion_force

            # Convert the resultant force to wheel speeds
            velocity = resultant_force.length
            angle = resultant_force.angle
            left_wheel = velocity + self.max_speed * math.sin(angle)
            right_wheel = velocity - self.max_speed * math.sin(angle)

            # Saturate wheel speeds
            left_wheel, right_wheel = self.saturate(left_wheel, right_wheel)

            # Set wheel speeds
            self.robot.epuck_wheels.set_speed(left_wheel, right_wheel)
        else:
            # If no neighbors, move randomly
            left_wheel = self.max_speed * (0.5 + random.uniform(-0.1, 0.1))
            right_wheel = self.max_speed * (0.5 + random.uniform(-0.1, 0.1))
            self.robot.epuck_wheels.set_speed(left_wheel, right_wheel)

        # No rays for plotting
        self.robot.variables.set_attribute("rays", "")

    def saturate(self, left, right):
        # Saturate Speeds greater than MAX_SPEED
        if left > self.max_speed:
            left = self.max_speed
        elif left < -self.max_speed:
            left = -self.max_speed

        if right > self.max_speed:
            right = self.max_speed
        elif right < -self.max_speed:
            right = -self.max_speed

        return left, right