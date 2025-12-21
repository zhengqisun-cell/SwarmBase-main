from comm.Serial import SerialController, DataType_Int, DataType_Float, DataType_Boolean
from input.JoystickManager import JoystickManager
import time

def send_preferences(serial, robot_mac, preferences):
    for pref in preferences:
        serial.send_preference(robot_mac, pref["data_type"], pref["key"], pref["value"])


ROBOT_MAC = ""
SERIAL_PORT = ""
PRINT_JOYSTICK = False

if __name__ == "__main__":
    # Communication
    serial = SerialController(SERIAL_PORT, timeout=.5)  # 5-second timeout
    # Common preferences that apply to all robots if any
    common_preferences = [
        {"data_type": DataType_Boolean, "key": "zEn", "value": True},
        {"data_type": DataType_Boolean, "key": "rollEn", "value": False},
        {"data_type": DataType_Boolean, "key": "rotateEn", "value": False},
        {"data_type": DataType_Boolean, "key": "pitchEn", "value": False},
        {"data_type": DataType_Boolean, "key": "yawEn", "value": True},

        {"data_type": DataType_Float, "key": "kpyaw", "value": 2},
        {"data_type": DataType_Float, "key": "kppyaw", "value": 0.03},
        {"data_type": DataType_Float, "key": "kdyaw", "value": 0.035},
        {"data_type": DataType_Float, "key": "kddyaw", "value": 0.03},
        {"data_type": DataType_Float, "key": "kiyaw", "value": 0},
        {"data_type": DataType_Float, "key": "kiyawrate", "value": 0},

        {"data_type": DataType_Float, "key": "yawrate_gamma", "value": 0.5},
        {"data_type": DataType_Float, "key": "rollrate_gamma", "value": 0.85},
        {"data_type": DataType_Float, "key": "pitchrate_gamma", "value": 0.7},

        {"data_type": DataType_Float, "key": "kpz", "value": 0.7},
        {"data_type": DataType_Float, "key": "kdz", "value": 1.2},
        {"data_type": DataType_Float, "key": "kiz", "value": 0},

        {"data_type": DataType_Float, "key": "kproll", "value": 0},
        {"data_type": DataType_Float, "key": "kdroll", "value": 0},
        {"data_type": DataType_Float, "key": "kppitch", "value": 0},
        {"data_type": DataType_Float, "key": "kdpitch", "value": -0.3},

        {"data_type": DataType_Float, "key": "z_int_low", "value": 0},
        {"data_type": DataType_Float, "key": "z_int_high", "value": 0.15},
        {"data_type": DataType_Float, "key": "yawRateIntRange", "value": 0},
        {"data_type": DataType_Float, "key": "lx", "value": 0.15},
        {"data_type": DataType_Float, "key": "servoRange", "value": 180},
        {"data_type": DataType_Float, "key": "servoBeta", "value": -90},
        {"data_type": DataType_Float, "key": "servo_move_min", "value": 0},
        {"data_type": DataType_Float, "key": "botZlim", "value": -1},
        {"data_type": DataType_Float, "key": "pitchOffset", "value": 0},
        {"data_type": DataType_Float, "key": "pitchInvert", "value": -1},

        {"data_type": DataType_Int, "key": "state_flag", "value": 0x40},
        {"data_type": DataType_Int, "key": "num_captures", "value": 2},
        {"data_type": DataType_Int, "key": "time_in_ball", "value": 500},
        {"data_type": DataType_Float, "key": "goal_height", "value": 8},

        {"data_type": DataType_Float, "key": "y_thresh", "value": 0.57},
        {"data_type": DataType_Float, "key": "y_strength", "value": 3.5},
        {"data_type": DataType_Float, "key": "x_strength", "value": 2},
        {"data_type": DataType_Float, "key": "fx_togoal", "value": 0.3},
        {"data_type": DataType_Float, "key": "fx_charge", "value": 0.5},
        {"data_type": DataType_Float, "key": "fx_levy", "value": 0.5},
        {"data_type": DataType_Int, "key": "n_max_x", "value": 240},
        {"data_type": DataType_Int, "key": "n_max_y", "value": 160},
        {"data_type": DataType_Float, "key": "h_ratio", "value": 0.8},
        {"data_type": DataType_Float, "key": "range_for_forward", "value": 0.12},

        {"data_type": DataType_Float, "key": "by_thresh", "value": 0.15},
        {"data_type": DataType_Float, "key": "by_strength", "value": 1.5},
        {"data_type": DataType_Float, "key": "bx_strength", "value": 1.1},
        {"data_type": DataType_Float, "key": "bfx_togoal", "value": 0.15},  # 0.11
        {"data_type": DataType_Float, "key": "bfx_charge", "value": 0.8},  # 0.4
        {"data_type": DataType_Float, "key": "bfx_levy", "value": .3},  # 0.3
        {"data_type": DataType_Int, "key": "bn_max_x", "value": 240},
        {"data_type": DataType_Int, "key": "bn_max_y", "value": 160},
        {"data_type": DataType_Float, "key": "bh_ratio", "value": 0.46},
        {"data_type": DataType_Float, "key": "brange_for_forward", "value": 0.15}
    ]

    # Sending common preferences to robot
    serial.manage_peer("A", ROBOT_MAC)
    serial.manage_peer("G", ROBOT_MAC)
    # Send common preferences
    send_preferences(serial, ROBOT_MAC, common_preferences)
    time.sleep(.2)

    # Joystick
    joystick = JoystickManager(1)

    sensors = serial.getSensorData()
    height = 0
    tz = 0
    if (sensors):
        tz = sensors[1]
        height = sensors[0]
    ready = 0
    old_a = 0
    old_b = 0
    old_x = 0
    fx_ave = 0
    dt = .1

    servos = 75

    try:
        while True:
            # Axis input: [left_vert, left_horz, right_vert, right_horz, left_trigger, right_trigger]
            # Button inputs: [A, B, X, Y]
            axis, buttons = joystick.getJoystickInputs()

            if buttons[3] == 1:  # y stops the program
                break
            if buttons[1] == 1 and old_b == 0:  # b pauses the control
                if (sensors):
                    tz = sensors[1]
                    height = sensors[0]
                if ready != 0:
                    ready = 0
                else:
                    ready = 1
            if buttons[2] == 1 and old_x == 0:
                if ready != 3:
                    ready = 3
                else:
                    ready = 4
            if buttons[0] == 1 and old_a == 0:
                ready = 2
            old_x = buttons[2]
            old_b = buttons[1]
            old_a = buttons[0]
            if PRINT_JOYSTICK:
                print(" ".join(["{:.1f}".format(num) for num in axis]), buttons)

            #### CONTROL INPUTS to the robot here #########
            if abs(axis[0]) < .15:
                axis[0] = 0
            height += -axis[0] * dt
            if height > 15:
                height = 15
            elif height < -3:
                height = -3

            if abs(axis[1]) < .15:
                axis[1] = 0
            tx = axis[1] * .2

            if abs(axis[4]) < .15:
                axis[4] = 0
            tz += -axis[4] * 1.2 * dt
            # tz = -axis[4] * .1

            fx = - axis[2] + axis[5]
            if (fx < 0):
                fx = fx * .5

            # print(tz, ":", height)
            # print(height)

            led = -buttons[2]
            ############# End CONTROL INPUTS ###############
            # fx = 0
            fz = height
            fx_ave = fx  # fx_ave * .8 + fx * .2
            # tx = 0
            # tz = 0
            # Send through serial port
            serial.send_control_params(ROBOT_MAC, (ready, fx_ave, fz, tx, tz, led, 0, 0, 0, 0, 0, 0, 0))
            time.sleep(dt)

    except KeyboardInterrupt:
        print("Stopping!")
    finally:
        serial.send_control_params(ROBOT_MAC, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
