import random

top = 50
alpha = 2
beta = 10
ignore_phase = 10
counter = 0
number_robot_sensed = 0
total = top + ignore_phase

def init():
    global counter, top
    counter = random.randint(0, top)
    robot.logprint("started synchronization_python")

def controlstep():
    global top, alpha, beta, ignore_phase, counter, number_robot_sensed, total
    process_rab()
    counter += 1

    if counter < top:
        #robot.range_and_bearing.set_data(1, 0)
        robot.epuck_range_and_bearing.set_data([1,0,0,0])
        if number_robot_sensed > 0:
            counter += alpha * counter / beta
            if counter >= top:
                counter = top - 1
    if counter >= top:
        robot.epuck_range_and_bearing.set_data([1,0,0,0])
        robot.epuck_leds.set_all_colors("red")
    if counter >= total:
        counter = 0
        robot.epuck_leds.set_all_colors("black")
        robot.epuck_range_and_bearing.set_data([0,0,0,0])

def process_rab():
    global number_robot_sensed 
    number_robot_sensed = 0
    for reading_i in robot.epuck_range_and_bearing.get_readings():
        if reading_i.data[1] == 1:
            number_robot_sensed += 1

def reset():
    global counter, top
    counter = random.randint(0, top)
    robot.logprint("reset")

def destroy():
	robot.logprint("destroy")