step_counter = 0

def init():
    global step_counter 
    step_counter = 0
    #robot.turret.set_speed_control_mode()
    #robot.turret.set_rotation_speed(10)
    robot.logprint("started gripping_python")

def controlstep():
    global step_counter
    step_counter += 1
    if step_counter < 70:
        robot.wheels.set_speed(5, 5)
    elif step_counter == 70:
        robot.wheels.set_speed(0, 0)
        robot.gripper.lock()
    elif step_counter < 120:
        robot.wheels.set_speed(-5, -5)
    elif step_counter < 170:
        robot.gripper.unlock()
    elif step_counter >= 170:
        robot.wheels.set_speed(0, 0)

def reset():
    global step_counter 
    step_counter = 0
    robot.logprint("reset")

def destroy():
	robot.logprint("destroy")