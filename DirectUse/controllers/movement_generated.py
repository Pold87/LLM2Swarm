#!/usr/bin/env python3

class CustomMovement:
    def __init__(self, robot, max_speed):
        """ Constructor
        :param robot: The robot instance
        :param max_speed: The maximum speed of the robot
        """
        self.robot = robot
        self.MAX_SPEED = max_speed
        self.timestep = 0

    def step(self):
        """ This method runs in every timestep """
        if 0 <= self.timestep < 100:
            # Spin clockwise
            self.robot.epuck_wheels.set_speed(self.MAX_SPEED, -self.MAX_SPEED)
        elif 100 <= self.timestep < 125:
            # Pause
            self.robot.epuck_wheels.set_speed(0, 0)
        elif 125 <= self.timestep < 225:
            # Spin counterclockwise
            self.robot.epuck_wheels.set_speed(-self.MAX_SPEED, self.MAX_SPEED)
        else:
            # Reset the timestep to loop the behavior
            self.timestep = -1
        
        # Increment the timestep
        self.timestep += 1