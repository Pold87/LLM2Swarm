#!/usr/bin/env python3
# This is the main control loop running in each argos robot

import math

NO_TURN = 0
SOFT_TURN = 1
HARD_TURN = 2

turning_mechanism = NO_TURN

hard_turn_angle_threshold = 90 * math.pi / 180
soft_turn_angle_threshold = 70 * math.pi / 180
no_turn_angle_threshold = 10 * math.pi / 180

max_speed = 10

target_distance = 75
gain = 1000
exponent = 2

def init():
    global turning_mechanism
    turning_mechanism = NO_TURN
    robot.colored_blob_omnidirectional_camera.enable()
    robot.leds.set_single_color(12, "red")
    robot.logprint("started aggregation 1 python")

def controlstep():
    global max_speed, NO_TURN, SOFT_TURN, HARD_TURN, no_turn_angle_threshold, soft_turn_angle_threshold, hard_turn_angle_threshold, turning_mechanism
    vector_light = vector_to_light()
    vector_flocking = flocking_vector()

    tot_speed = vector_light["length"] + vector_flocking["length"]
    tot_angle = vector_light["angle"] + vector_flocking["angle"]

    if tot_speed > max_speed:
        tot_speed = max_speed
    
    if math.fabs(tot_angle) <= no_turn_angle_threshold:
        turning_mechanism = NO_TURN
    elif math.fabs(tot_angle) > hard_turn_angle_threshold:
        turning_mechanism = HARD_TURN
    elif turning_mechanism == NO_TURN and math.fabs(tot_angle) > soft_turn_angle_threshold:
        turning_mechanism = SOFT_TURN

    speed1 = 0
    speed2 = 0
    if turning_mechanism == NO_TURN:
        speed1 = tot_speed
        speed2 = tot_speed
    elif turning_mechanism == SOFT_TURN:
        speed_factor = (hard_turn_angle_threshold - math.fabs(tot_angle))/hard_turn_angle_threshold
        speed1 = tot_speed - tot_speed * (1 - speed_factor)
        speed2 = tot_speed + tot_speed + (1 - speed_factor)
    elif turning_mechanism == HARD_TURN:
        speed1 = -max_speed
        speed2 = max_speed

    if tot_angle > 0:
        robot.wheels.set_speed(speed1, speed2)
    else:
        robot.wheels.set_speed(speed2, speed1)

def vector_to_light():
    global turning_mechanism, max_speed
    light_readings = robot.light_sensor.get_readings()
    accumulator = {"x": 0, "y": 0}

    for light_reading_i in light_readings:
        accumulator["x"] += light_reading_i.value * math.cos(light_reading_i.angle.value()) 
        accumulator["y"] += light_reading_i.value * math.sin(light_reading_i.angle.value())

    tot_angle = math.atan2(accumulator["y"], accumulator["x"])
    tot_length = math.sqrt(accumulator["x"] * accumulator["x"] + accumulator["y"] * accumulator["y"])

    if tot_length > 0:
        tot_length = 0.25 * max_speed
    return {"length": tot_length, "angle": tot_angle}

def flocking_vector():
    global target_distance, max_speed
    camera_readings = robot.colored_blob_omnidirectional_camera.get_readings()
    accumulator = {"x": 0, "y": 0}
    flj = 0
    num_blobs_seen = 0.1

    if len(camera_readings) > 0: 
        for reading_i in camera_readings:
            if reading_i.color == lib.color("red").raw_color and \
                reading_i.distance < target_distance * 1.8:

                flj = lennardjones(reading_i.distance)

                accumulator["x"] += flj * math.cos(reading_i.angle.value()) 
                accumulator["y"] += flj * math.sin(reading_i.angle.value())
                num_blobs_seen += 1
        

        tot_angle = math.atan2(accumulator["y"], accumulator["x"])
        tot_length = math.sqrt(accumulator["x"] * accumulator["x"] + accumulator["y"] * accumulator["y"]) / num_blobs_seen
        if tot_length > max_speed:
            tot_length = max_speed
        return {"length": tot_length, "angle": tot_angle}
    else:
        return {"length": 0, "angle": 0}

def lennardjones(distance):
    global gain, target_distance, exponent
    return -(4*gain/distance * (math.pow(target_distance/distance,exponent*exponent) - math.pow(target_distance/distance,exponent)))

def reset():
    global turning_mechanism
    turning_mechanism = NO_TURN
    robot.logprint("reset")

def destroy():
	robot.logprint("destroy")