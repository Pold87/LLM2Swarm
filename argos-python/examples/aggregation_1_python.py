import random, math

WALK = "WALK"
AVOID = "AVOID"
GO_FWD = "GO_FWD"
STOP = "STOP"

current_state = WALK
is_obstacle_sensed = False
is_black_sensed = False

MAX_TURN_STEPS = 20
current_turn_steps = 0

FWD_STEPS = 40
current_fwd_steps = 0

def init():
    global current_state
    current_state = WALK
    robot.logprint("started aggregation_1_python")

def controlstep():
    global current_state, current_fwd_steps, current_turn_steps, is_black_sensed, is_obstacle_sensed
    global WALK, AVOID, GO_FWD, STOP, FWD_STEPS

    process_prox()
    process_ground()

    if current_state == WALK:
        robot.wheels.set_speed(10, 10)
        if is_obstacle_sensed:
            current_state = AVOID
            current_turn_steps = random.randint(0, MAX_TURN_STEPS)
        elif is_black_sensed:
            current_state = GO_FWD
            current_fwd_steps = FWD_STEPS
    elif current_state == AVOID:
        robot.wheels.set_speed(-10, 10)
        current_turn_steps -= 1
        if current_turn_steps <= 0:
            current_state = WALK

    elif current_state == GO_FWD:
        current_fwd_steps -= 1
        robot.wheels.set_speed(10, 10)
        if current_fwd_steps <= 0 or is_obstacle_sensed or not(is_black_sensed):
            current_state = STOP

    elif current_state == STOP:
        robot.wheels.set_speed(0, 0)

def process_prox():
    global is_obstacle_sensed
    is_obstacle_sensed = False
    readings = robot.proximity.get_readings()
    max_reading = max(readings, key = lambda x: x.value)
    if max_reading.value > 0.05 and math.fabs(max_reading.angle.value()) < math.pi / 2:
        is_obstacle_sensed = True

def process_ground():
    global is_black_sensed
    is_black_sensed = False
    ground_readings = robot.base_ground.get_readings()
    min_reading = min(ground_readings, key = lambda x: x.value)
    if min_reading.value == 0:
        is_black_sensed = True



def reset():
    current_state = WALK
    is_obstacle_sensed = False
    is_black_sensed = False
    current_turn_steps = 0
    current_fwd_steps = 0
    robot.logprint("reset")

def destroy():
	robot.logprint("destroy")