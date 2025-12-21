

from comm.Serial import SerialController, DataType_Int, DataType_Float, DataType_Boolean
from input.JoystickManager import JoystickManager
from gui.simpleGUI import SimpleGUI
from user_parameters import ROBOT_MAC, SERIAL_PORT, PRINT_JOYSTICK

import time







BaseStationAddress = "" # you do not need this, just make sure your DroneMacAddress is not your base station mac address



if __name__ == "__main__":
    # Communication
    serial = SerialController(SERIAL_PORT, timeout=.5)  # .5-second timeout
    serial.manage_peer("A", ROBOT_MAC)
    serial.manage_peer("G", ROBOT_MAC)
    time.sleep(.05)
    serial.send_preference(ROBOT_MAC, DataType_Boolean, "zEn", False)
    serial.send_preference(ROBOT_MAC, DataType_Boolean, "yawEn", True)

    # // PID terms
    serial.send_preference(ROBOT_MAC, DataType_Float, "kpyaw", 1.5) #2
    serial.send_preference(ROBOT_MAC, DataType_Float, "kdyaw", .1)#.1
    serial.send_preference(ROBOT_MAC, DataType_Float, "kiyaw", 0)

    serial.send_preference(ROBOT_MAC, DataType_Float, "kpz", 0.3)
    serial.send_preference(ROBOT_MAC, DataType_Float, "kdz", 0.6)
    serial.send_preference(ROBOT_MAC, DataType_Float, "kiz", 0.1)
    
    # // Range terms for the integral
    serial.send_preference(ROBOT_MAC, DataType_Float, "z_int_low", 0.05)
    serial.send_preference(ROBOT_MAC, DataType_Float, "z_int_high", 0.15)
    

    # Allows the robot to read the parameters from flash memory to be used.
    serial.send_control_params(ROBOT_MAC, (0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 1, 0))

    time.sleep(.2)

    # Joystick
    joystick = JoystickManager()
    mygui = SimpleGUI()
    
    ready = 1
    old_b = 0
    old_x = 0
    dt = .1
    height = 0
    servos = 75
    tz = 0
    try:
        while True:
            # Axis input: [left_vert, left_horz, right_vert, right_horz, left_trigger, right_trigger]
            # Button inputs: [A, B, X, Y]
            axis, buttons = joystick.getJoystickInputs()
            
            if buttons[3] == 1: # y stops the program
                break

            # b button is a toggle which changes the ready state
            if buttons[1] == 1 and old_b == 0: # b pauses the control
                if ready != 0:
                    ready = 0
                else:
                    ready = 1
            old_b = buttons[1]


            if PRINT_JOYSTICK:
                print("Joystick: ", ["{:.1f}".format(num) for num in axis], "Buttons: ", buttons)

            #### CONTROL INPUTS to the robot here #########
            fx = (axis[5]+1) / 2 - (axis[4]+1) / 2  # Forward with the triggers
            fz = -axis[0]  # Vertical left joystick
            tx = 0  # No roll control
            tz = axis[3]  # Horizontal right joystick
            led = -buttons[2]  # Button X

            print("fx={:.2f} fz={:.2f} tz={:.2f} LED={:.2f} ".format(fx, fz, tz, led), end=' ')
            ############# End CONTROL INPUTS ###############
            sensors = serial.getSensorData()
            #
            if sensors:
                print("Sensors:", ["{:.2f}".format(val) for val in sensors])
                mygui.update(
                    cur_yaw=sensors[1],
                    des_yaw=tz,
                    cur_height=sensors[0],
                    des_height=height,
                    battery=sensors[2],
                    distance=sensors[3],
                    connection_status=True,
                )
            else:
                print("No sensors")



            # Send through serial port
            serial.send_control_params(ROBOT_MAC, (ready, fx, fz, tx, tz, led, 0, 0, 0, 0, 0, 0, 0))
            time.sleep(dt)
            
    except KeyboardInterrupt:
        print("Stopping!")
        # Send zero input
serial.send_control_params(ROBOT_MAC, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
