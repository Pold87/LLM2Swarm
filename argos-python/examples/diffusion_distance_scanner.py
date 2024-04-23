import math

# PARAMETERS:

# Maximum tolerance for the angle between
# the robot heading direction and
# the closest obstacle detected. 
alpha = 7.5 * math.pi / 180
# Maximum tolerance for the proximity reading between
# the robot and the closest obstacle.
# The proximity reading is 0 when nothing is detected
# and grows exponentially to 1 when the obstacle is
# touching the robot.
delta = 0.1
# Wheel speed.
wheel_velocity = 5
# Angle tolerance range to go straight.
# It is set to [-alpha,alpha]. 
go_straight_angle_range = [-alpha, alpha]

def init():
    robot.distance_scanner.enable()
    robot.distance_scanner.set_rpm(30)
    robot.distance_scanner.set_angle(60)
    robot.logprint("started diffusion1_python")

def controlstep():
    global alpha, delta, wheel_velocity, go_straight_angle_range

    accumulator = {"x": 0, "y": 0}
    # Get readings from the proximity sensors
    proximity_readings = robot.proximity.get_readings()

    distance_readings = robot.distance_scanner.get_short_readings()
    for i in distance_readings:
        print(i.data())


    
    for proximity_reading_i in proximity_readings:
        accumulator["x"] += proximity_reading_i.value * math.cos(proximity_reading_i.angle.value()) 
        accumulator["y"] += proximity_reading_i.value * math.sin(proximity_reading_i.angle.value())

    tot_angle = math.atan2(accumulator["y"], accumulator["x"])
    tot_length = math.sqrt(accumulator["x"] * accumulator["x"] + accumulator["y"] * accumulator["y"]) / 24

    if (go_straight_angle_range[0] <= tot_angle and tot_angle <= go_straight_angle_range[1] and \
       tot_length < delta):
        robot.wheels.set_speed(wheel_velocity, wheel_velocity)
    else:
        if tot_angle > 0:
            robot.wheels.set_speed(wheel_velocity, 0)
        else:
            robot.wheels.set_speed(0, wheel_velocity)

def reset():
    robot.distance_scanner.enable()
    robot.distance_scanner.set_rpm(30)
    robot.distance_scanner.set_angle(60)
    robot.logprint("reset")

def destroy():
	robot.logprint("destroy")