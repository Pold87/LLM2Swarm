import random


counter = 0

top = 50

def init():
    global counter, top
    counter = random.randint(0, top)
    robot.logprint("started synchronization_python")
    robot.colored_blob_omnidirectional_camera.enable()

def controlstep():
    global counter
    readings = robot.colored_blob_omnidirectional_camera.get_readings()
    
    someone_flashed = False
    i = 0
    while (not someone_flashed and i < len(readings)):
        someone_flashed = (readings[i].color == lib.color("red").raw_color)
        if someone_flashed:
            print(someone_flashed)
        i += 1
    
    if someone_flashed:
        counter += counter / 10
        
    else:
        counter += 1

    if counter > top:
        robot.leds.set_all_colors("red")
        counter = 0
    else:
        robot.leds.set_all_colors("black")


def reset():
    global counter
    counter = random.randint(0, top)
    robot.logprint("reset")

def destroy():
	robot.logprint("destroy")