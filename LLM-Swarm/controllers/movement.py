#!/usr/bin/env python3
import random, math
import time
import logging
from aux import Vector2D

class GPS(object):
    """ GPS-based positioning sensor
    """

    def __init__(self, robot):
        """ Constructor
        """
        # Robot class
        self.robot = robot

    def getOrientation(self, degrees = False):

        if degrees:
            return math.degrees(self.robot.position.get_orientation())
        else:
            return self.robot.position.get_orientation()

    def getPosition(self):
        return Vector2D(self.robot.position.get_position()) 



class Odometry(object):
    """ Odometry-based positioning sensor
    """

    def __init__(self, robot, bias = 0):
        """ Constructor
        :type range: int
        :param enode: Random-Walk speed (tip: 500)
        """
        # Robot class
        self.robot = robot

        # Fixed Parameters
        self.L = 0.053          # Distance between wheels
        self.R = 0.0205         # Wheel radius

        # Internal variables 
        self.pos = Vector2D(self.robot.position.get_position())  
        self.ori = self.robot.position.get_orientation()

    def step(self):       

        # Read odometry sensor
        dleft, dright = self.robot.differential_steering.get_distances() 
        dleft, dright = dleft * 0.01, dright * 0.01

        # If going straight
        if abs(dleft-dright) < 1e-6:
            dt = 0
            dx = 0.5*(dleft+dright) * math.cos(self.ori) 
            dy = 0.5*(dleft+dright) * math.sin(self.ori) 

        # If rotating or curving
        else:
            dr  = (dleft+dright)/(2*(dright-dleft)) * self.L

            dt = (dright - dleft) / self.L 
            dx =  dr * math.sin(dt+self.ori) - dr * math.sin(self.ori)
            dy = -dr * math.cos(dt+self.ori) + dr * math.cos(self.ori)

        # Update position and orientation estimates
        self.ori  = (self.ori + dt) % math.pi
        self.pos += Vector2D(dx,dy)

    def setOrientation(self, orientation = 0):
        self.ori = orientation

    def setPosition(self, position = [0,0]):
        self.pos = position

    def getOrientation(self):
        return self.ori

    def getPosition(self):
        return self.pos

class OdoCompass(object):
    """ Odometry-based positioning sensor with compass
    """

    def __init__(self, robot, bias = 0, variance = 0):
        """ Constructor
        :type range: int
        :param enode: Random-Walk speed (tip: 500)
        """
        # Robot class
        self.robot = robot

        # Fixed Parameters
        self.L = 0.053          # Distance between wheels
        self.R = 0.0205         # Wheel radius

        # Internal variables 
        self.pos = Vector2D(self.robot.position.get_position())  
        self.ori = self.robot.position.get_orientation()

    def step(self):       

        # Read odometry sensor 
        dl, dr = self.robot.differential_steering.get_distances()
        dl, dr = dl * 0.01, dr * 0.01

        # Read compass sensor
        dt = self.robot.position.get_orientation() - self.ori

        # Add noise to readings
        dl += random.gauss(0, 0.01)
        dr += random.gauss(0, 0.01)
        dt += random.gauss(0, math.radians(0))

        # Calculate delta in position
        dx = (dl+dr)/2 * math.cos(self.ori + dt/2) 
        dy = (dl+dr)/2 * math.sin(self.ori + dt/2) 

        # Update position and orientation estimates
        self.ori += dt 
        self.pos += Vector2D(dx,dy)

    def setOrientation(self):
        self.ori = self.robot.position.get_orientation()

    def setPosition(self):
        self.pos = Vector2D(self.robot.position.get_position())

    def getOrientation(self):
        return self.ori

    def getPosition(self):
        return self.pos

class Navigate(object):
    """ Set up a Navigation loop on a background thread
    The __navigating() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, robot, MAX_SPEED):
        """ Constructor
        :type range: int
        :param enode: Random-Walk speed (tip: 500)
        """
        self.robot = robot
        self._id = str(int(robot.variables.get_id()[2:])+1)

        # Internal variables
        self.__stop = False
        self.__walk = True
        self.__distance_to_target = 0
        self.__window = []
        self.__distance_traveled = 0
        self.__old_vec  = 0
        self.__old_time = 0
        self.__accumulator_I = 0
        self.__accumulator_stuck = 0

        # Fixed Parameters
        self.MAX_SPEED = MAX_SPEED        # Maximum robot speed
        self.L = 0.053                    # Distance between wheels
        self.R = 0.0205                   # Wheel radius

        # Navigation parameters
        self.Kp = 50                                    # Angular velocity proportional gain
        self.window_size = 10                           # Avoid vector filtering           
        self.thresh = math.radians(70)                  # Wait before moving
        self.thresh_front_collision = math.radians(15)  # Aggressive avoidance

        # Obstacle avoidance parameters
        self.thresh_ir    = 0
        self.weights      = 25*[-10, -10, 0, 0, 0, 0, 10, 10]

        # Vectorial obstacle avoidance parameters
        self.Ki = 0.1

    def update_state(self, target = [0,0]):

        self.position = Vector2D(self.robot.position.get_position()[0:2])
        self.orientation = self.robot.position.get_orientation()
        self.target = Vector2D(target)

    def navigate(self, target = [0,0]):

        # Update the current position, orientation and target of the robot
        self.update_state(target = target)
        
        # Calculate the local frame vector to the desired target
        vec_target = (self.target-self.position).rotate(-self.orientation)
        

        T = vec_target.normalize()

        # The desired vector (we only care about direction)
        D = T

        self.update_rays(Vector2D(0,0),Vector2D(0,0),D)

        dotProduct = 0
        # The target angle is behind the robot, we just rotate, no forward motion
        if D.angle > self.thresh or D.angle < -self.thresh:
            dotProduct = 0

        # Else, we project the forward motion vector to the desired angle
        else:
            dotProduct = Vector2D(1,0).dot(D.normalize())

        # The angular velocity component is the desired angle scaled linearly
        angularVelocity = self.Kp * D.angle

        # The final wheel speeds are computed combining the forward and angular velocities
        right = dotProduct * self.MAX_SPEED/2 - angularVelocity * self.L
        left = dotProduct * self.MAX_SPEED/2 + angularVelocity * self.L

        # Set wheel speeds
        self.robot.epuck_wheels.set_speed(right, left)

        # Store the distance to arrive at target
        self.__distance_to_target = abs(vec_target)

    def navigate_with_obstacle_avoidance(self, target = [0,0]):

        # Update the current position, orientation and target of the robot
        self.update_state(target = target)
        
        # Calculate the local frame vector to the desired target
        vec_target = (self.target-self.position).rotate(-self.orientation)

        # Calculate the local frame vector to the avoid objects
        acc = Vector2D()
        prox_readings = self.robot.epuck_proximity.get_readings()

        for reading in prox_readings:
            acc += Vector2D(reading.value, reading.angle.value(), polar = True)

        # Generate a time window to have smoother variations on the avoid vector
        self.__window.append(acc)
        if len(self.__window) > self.window_size:
            self.__window.pop(0)
        
        vec_avoid = (1/self.window_size) * sum(self.__window, start = Vector2D()) 

        if abs(vec_avoid) < 0.01:
            self.__window = []

        # Normalize and weight to obtain desired control behavior
        T = 0.2 * vec_target.normalize()
        A = 0.5 * -vec_avoid#.normalize()

        # Saturate the avoid angle
        if abs(A.angle) > math.radians(90):
            A = Vector2D(A.length, math.copysign(math.radians(90), A.angle), polar = True)

        # # Integral action on the avoid could make sense
        # def trapz(new_time, new_vec):
        #     trap = 0.5 * (new_vec + self.__old_vec)
        #     self.__accumulator_I += self.Ki * trap
        #     self.__old_vec = new_vec
        #     self.__old_time = new_time

        # trapz(time.time(), A.length)

        # if abs(A) < 0.01:
        #     self.__accumulator_I = 0

        # elif self.__accumulator_I > 1:
        #     self.__accumulator_I = 1

        # # Calculate the local frame vector to the desired motion (target + avoid)
        # A = A + self.__accumulator_I*A


        # The desired vector (we only care about direction)
        D =  (T + A)

        self.update_rays(T,A,D)

        dotProduct = 0
        # The target angle is behind the robot, we just rotate, no forward motion
        if D.angle > self.thresh or D.angle < -self.thresh:
            dotProduct = 0

        # Else, we project the forward motion vector to the desired angle
        else:
            dotProduct = Vector2D(1,0).dot(D.normalize())

        # The angular velocity component is the desired angle scaled linearly
        angularVelocity = self.Kp * D.angle

        # The final wheel speeds are computed combining the forward and angular velocities
        right = dotProduct * self.MAX_SPEED/2 - angularVelocity * self.L
        left = dotProduct * self.MAX_SPEED/2 + angularVelocity * self.L

        # # Saturate wheel speeds
        # left, right = self.saturate(left, right)

        # # Aggressive avoidance for frontal collisions
        # if  vec_avoid.length > 0.01 and abs(vec_avoid.angle) < self.thresh_front_collision:
        #     print(math.degrees(vec_avoid.angle), "Front Collision")
        #     # left, right = self.avoid(left, right)

        # Set wheel speeds
        self.robot.epuck_wheels.set_speed(right, left)

        # Store the distance to arrive at target
        self.__distance_to_target = abs(vec_target)

    def update_rays(self, T, A, D):
        # Change to global coordinates for the plotting

        self.robot.variables.set_attribute("rays", self._id 
                                            + ', ' + repr(self.position) 
                                            + ', ' + repr(T.rotate(self.orientation)) 
                                            + ', ' + repr(A.rotate(self.orientation))
                                            + ', ' + repr(D.rotate(self.orientation)) 
                                            +'\n')

    def avoid(self, left = 0, right = 0, move = False):
        obstacle = False
        avoid_left = avoid_right = 0

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

    def avoid_static(self, left = 0, right = 0, move = False):

        # Update the current position, orientation and target of the robot
        self.update_state()
        
        # Calculate the local frame vector to the avoid objects
        acc = Vector2D()
        prox_readings = self.robot.epuck_proximity.get_readings()

        for reading in prox_readings:
            acc += Vector2D(reading.value, reading.angle.value(), polar = True)

        # Project the forward motion vector to the desired angle
        dotProduct = Vector2D(1,0).dot(acc.normalize())
        
        # The angular velocity component is the desired angle scaled linearly
        angVelocity = self.Kp * acc.angle

        # The final wheel speeds are computed combining the forward and angular velocities
        right = dotProduct * self.MAX_SPEED/2 - angVelocity * self.L
        left = dotProduct * self.MAX_SPEED/2 + angVelocity * self.L

        if move:
            self.robot.epuck_wheels.set_speed(right, left)

        return left, right


    def stop(self):
        robot.epuck_wheels.set_speed(0,0)

    def set_wheels(self, right, left):
        robot.epuck_wheels.set_speed(right,left)

    def get_distance_to(self, to):

        # Update the current position, orientation and target of the robot
        self.update_state(target = to)

        # Return the distance to
        return abs(self.target-self.position)


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


    def avoid_vec_lua(self, left, right):
    # Obstacle avoidance; translated from Lua
    # Source: swarm intelligence examples

        accumul = Vector2D(0,0)

        readings = self.robot.epuck_proximity.get_readings()
        
        for reading in readings:

            # We calculate the x and y components given length and angle
            vec = Vector2D(reading.value, reading.angle.value(), polar = True)

            # We sum the vectors into a variable called accumul
            accumul += vec

        # We get length and angle of the final sum vector
        length, angle = accumul.to_polar()

        if length > 0.01:
            # print(length)
            # If the angle is greater than 0 the resulting obstacle is on the left. 
            # Otherwise it is on the right
            # We turn with a speed that depends on the angle. 
            # The closer the obstacle to the x axis of the robot, the quicker the turn
            speed = max(0.5, math.cos(angle)) * self.MAX_SPEED

            if angle > 0:
                right = speed
                left = 0
            else:
                right = 0
                left = speed

        return left, right


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

    # def avoid(self, left, right):

    #     # Obstacle avoidance
    #     readings = self.robot.epuck_proximity.get_readings()
    #     self.ir = [reading.value for reading in readings]
                
    #     # Find Wheel Speed for Obstacle Avoidance
    #     for i, reading in enumerate(self.ir):
    #         if (reading > self.thresh_ir):
    #             left  = self.MAX_SPEED/2 + self.weights_left[i] * reading
    #             right = self.MAX_SPEED/2 + self.weights_right[i] * reading

    #     return left, right

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
        
    def avoid_vec_lua_erb(self, left, right):
        # Obstacle avoidance; translated from LUA
        # Source: swarm intelligence ULB course

        accumul = Vector2D(0,0)

        pos = tuple(self.robot.position.get_position()[0:2])
        ori = self.robot.position.get_orientation()

        readings = self.robot.epuck_range_and_bearing.get_readings()
        
        for reading in readings:

            # if reading[2] < math.radians(15):
            #     continue

            # else:
            # We calculate the x and y components given length and angle
            vec = Vector2D(reading[1]/100, reading[2]+ori, polar=True)

            # We sum the vectors into a variable called accumul
            accumul += vec

        # We get length and angle of the final sum vector
        length, angle = accumul.to_polar()
        # print(length, angle)

        if 0.05 < length < 0.1:
            # If the angle is greater than 0 the resulting obstacle is on the left. 
            # Otherwise it is on the right
            # We turn with a speed that depends on the angle. 
            # The closer the obstacle to the x axis of the robot, the quicker the turn
            speed = max(0.5, math.cos(angle)) * self.MAX_SPEED
            if angle > 0:
                right = speed
                left = 0
            else:
                right = 0
                left = speed

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




	
 # def navigate(self, location = [0,0]):

 #        position_error = Vector2D(location)-Vector2D(self.robot.position.get_position()[0:2])

 #        orientation_current = self.robot.position.get_orientation()
 #        _, orientation_desired = position_error.to_polar()
 #        orientation_error = math.atan2(math.sin(orientation_desired-orientation_current), math.cos(orientation_desired-orientation_current))
        
 #        # Tune controller rules here
 #        orientation_error_dot = -self.Kp * orientation_error

 #        # Find Wheel Speed for navigation
 #        v = 0
 #        if abs(orientation_error) < self.thresh:
 #            # v = math.sqrt(position_error[0]**2 + position_error[1]**2)
 #            v = self.MAX_SPEED/2
            
 #        right = (2*v + self.L*orientation_error_dot) / (2*self.R)
 #        left = (2*v - self.L*orientation_error_dot) / (2*self.R)

 #        left, right = self.saturate(left, right, 2)

 #        # Avoid Obstacles
 #        left, right = self.avoid_argos3_example(left, right)
 #        left, right = self.saturate(left, right, 1)

 #        # Set wheel speeds
 #        self.robot.epuck_wheels.set_speed(right, left)
 #        self.__hasArrived = abs(position_error) < 0.05


 #    def flocking_argos_python_example(self):
 #        NO_TURN = 0
 #        SOFT_TURN = 1
 #        HARD_TURN = 2

 #        turning_mechanism = NO_TURN

 #        hard_turn_angle_threshold = 90 * math.pi / 180
 #        soft_turn_angle_threshold = 70 * math.pi / 180
 #        no_turn_angle_threshold = 10 * math.pi / 180

 #        max_speed = 10

 #        target_distance = 0.2
 #        gain = 1000
 #        exponent = 2

 #        def lennard_jones(distance):
 #            return -(4*gain/distance * (math.pow(target_distance/distance,exponent*exponent) - math.pow(target_distance/distance,exponent)))

 #        def vector_to_light():

 #            position_current = Vector2D(self.robot.position.get_position()[0], self.robot.position.get_position()[1])
 #            position_desired = Vector2D(0,0)
 #            position_error = position_desired-position_current

 #            tot_length, tot_angle = position_error.to_polar()

 #            if tot_length > 0:
 #                tot_length = 0.25 * max_speed

 #            return {"length": tot_length, "angle": tot_angle}

 #        def flocking_vector():

 #            erb_readings = self.robot.epuck_range_and_bearing.get_packets()
 #            accumulator = {"x": 0, "y": 0}
 #            flj = 0
 #            num_blobs_seen = 0.1

 #            if erb_readings:
 #                for reading in erb_readings:
 #                    if reading.range/100 < target_distance * 1.8:

 #                        flj = lennard_jones(reading.range/100)

 #                        ori = self.robot.position.get_orientation()

 #                        accumulator["x"] += flj * math.cos(reading.bearing.value()+ori) 
 #                        accumulator["y"] += flj * math.sin(reading.bearing.value()+ori)
 #                        num_blobs_seen += 1

 #                tot_angle = math.atan2(accumulator["y"], accumulator["x"])
 #                tot_length = math.sqrt(accumulator["x"] * accumulator["x"] + accumulator["y"] * accumulator["y"]) / num_blobs_seen

 #                if tot_length > max_speed:
 #                    tot_length = max_speed

 #                return {"length": tot_length, "angle": tot_angle}
 #            else:
 #                return {"length": 0, "angle": 0}

 #        vector_light = vector_to_light()

 #        vector_flocking = flocking_vector()

 #        tot_speed = vector_light["length"] + vector_flocking["length"]
 #        tot_angle = vector_light["angle"] + vector_flocking["angle"]

 #        if tot_speed > max_speed:
 #            tot_speed = max_speed
        
 #        if math.fabs(tot_angle) <= no_turn_angle_threshold:
 #            turning_mechanism = NO_TURN
 #        elif math.fabs(tot_angle) > hard_turn_angle_threshold:
 #            turning_mechanism = HARD_TURN
 #        elif turning_mechanism == NO_TURN and math.fabs(tot_angle) > soft_turn_angle_threshold:
 #            turning_mechanism = SOFT_TURN

 #        speed1 = 0
 #        speed2 = 0
 #        if turning_mechanism == NO_TURN:
 #            speed1 = tot_speed
 #            speed2 = tot_speed
 #        elif turning_mechanism == SOFT_TURN:
 #            speed_factor = (hard_turn_angle_threshold - math.fabs(tot_angle))/hard_turn_angle_threshold
 #            speed1 = tot_speed - tot_speed * (1 - speed_factor)
 #            speed2 = tot_speed + tot_speed + (1 - speed_factor)
 #        elif turning_mechanism == HARD_TURN:
 #            speed1 = -max_speed
 #            speed2 = max_speed

 #        if tot_angle > 0:
 #            self.robot.epuck_wheels.set_speed(speed1, speed2)
 #            # left, right = speed1, speed2
 #        else:
 #            self.robot.epuck_wheels.set_speed(speed2, speed1)

 #    def pattern_formation_swarm_intelligence(self, target = None):
 #        TARGET_DIST = 10 # -- the target distance between robots, in cm
 #        EPSILON = 50 # -- a coefficient to increase the force of the repulsion/attraction function
 #        WHEEL_SPEED = 5 # -- max wheel speed

 #        #---------------------------------------------------------------------------

 #        # ---------------------------------------------------------------------------
 #        # --This function computes the necessary wheel speed to go in the direction of the desired angle.
 #        def ComputeSpeedFromAngle(angle):
 #            dotProduct = 0
 #            KProp = 20
 #            wheelsDistance = 0.053

 #            # -- if the target angle is behind the robot, we just rotate, no forward motion
 #            if angle > math.pi/2 or angle < -math.pi/2:
 #                dotProduct = 0
 #            else:
 #            # -- else, we compute the projection of the forward motion vector with the desired angle
 #                forwardVector = [math.cos(0), math.sin(0)]
 #                targetVector = [math.cos(angle), math.sin(angle)]
 #                dotProduct = forwardVector[0]*targetVector[0]+forwardVector[1]*targetVector[1]

 #             # -- the angular velocity component is the desired angle scaled linearly
 #            angularVelocity = KProp * angle;
 #            # -- the final wheel speeds are compute combining the forward and angular velocities, with different signs for the left and right wheel.
 #            speeds = [dotProduct * WHEEL_SPEED - angularVelocity * wheelsDistance, dotProduct * WHEEL_SPEED + angularVelocity * wheelsDistance]

 #            return speeds
 #        # ---------------------------------------------------------------------------

 #        # ---------------------------------------------------------------------------
 #        # -- In this function, we take all distances of the other robots and apply the lennard-jones potential.
 #        # -- We then sum all these vectors to obtain the final angle to follow in order to go to the place with the minimal potential
 #        def ProcessRAB_LJ(target):

 #            sum_vector = [0,0]
 #            erb_readings = self.robot.epuck_range_and_bearing.get_packets()

 #            for reading in erb_readings: #do -- for each robot seen
 #                lj_value = 0.1*ComputeLennardJonesRep(reading.range) # -- compute the lennard-jones value
 #                sum_vector[0] = sum_vector[0] + math.cos(reading.bearing.value())*lj_value # -- sum the x components of the vectors
 #                sum_vector[1] = sum_vector[1] + math.sin(reading.bearing.value())*lj_value # -- sum the y components of the vectors

 #            if target:
 #                x, y = self.robot.position.get_position()[0], self.robot.position.get_position()[1]
 #                theta = self.robot.position.get_orientation()

 #                position = Vector2D(x,y)
 #                target = Vector2D(target[0],target[1])
 #                vec_to_target = target-position
 #                mag, ang = vec_to_target.to_polar()


 #                lj_value = 10*ComputeLennardJones(mag*100)
 #                sum_vector[0] = sum_vector[0] + math.cos(ang-theta)*lj_value # -- sum the x components of the vectors
 #                sum_vector[1] = sum_vector[1] + math.sin(ang-theta)*lj_value # -- sum the y components of the vectors

 #            desired_angle = math.atan2(sum_vector[1],sum_vector[0]) # -- compute the angle from the vector
 #            # --log( "angle: "..desired_angle.." length^2: "..(math.pow(sum_vector[1],2)+math.pow(sum_vector[2],2)) )
 #            return desired_angle

 #        # ---------------------------------------------------------------------------

 #        # ---------------------------------------------------------------------------
 #        # -- This function take the distance and compute the lennard-jones potential.
 #        # -- The parameters are defined at the top of the script
 #        def ComputeLennardJones(distance):
 #           return -(4*EPSILON/distance * (math.pow(TARGET_DIST/distance,4) - math.pow(TARGET_DIST/distance,2)))

 #        def ComputeLennardJonesRep(distance):
 #           return -(4*EPSILON/distance * (math.pow(TARGET_DIST/distance,4)))

 #        #---------------------------------------------------------------------------

 #        target_angle = ProcessRAB_LJ(target) #-- then we compute the angle to follow, using the other robots as input, see function code for details
 #        speeds = ComputeSpeedFromAngle(target_angle) #-- we now compute the wheel speed necessary to go in the direction of the target angle
 #        # self.robot.wheels.set_velocity(speeds[1],speeds[2]) #-- actuate wheels to move
 #        self.robot.epuck_wheels.set_speed(speeds[0],speeds[1])

 #        self.__hasArrived = 0

 #        # robot.range_and_bearing.clear_data() #-- forget about all received messages for next step
 #        # ---------------------------------------------------------------------------
