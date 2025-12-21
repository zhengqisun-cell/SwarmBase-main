

from comm.Serial import SerialController, DataType_Int, DataType_Float, DataType_Boolean
from input.JoystickManager import JoystickManager
from gui.simpleGUI import SimpleGUI
from gui.niclaGUI import NiclaBox
import time
from user_parameters import SERIAL_PORT, PRINT_JOYSTICK

ROBOT_MAC = "34:85:18:AC:0E:30"#"34:85:18:AB:FE:68" # "DC:54:75:D7:B3:E8"
PASSIVE_ROBOT_MAC = "48:27:E2:E6:E0:1C"#48:27:E2:E6:E0:1C


if __name__ == "__main__":
    # Communication
    serial = SerialController(SERIAL_PORT, timeout=.5)  # 5-second timeout
    serial.manage_peer("A", ROBOT_MAC)
    serial.manage_peer("G", ROBOT_MAC)
    serial.manage_peer("A", PASSIVE_ROBOT_MAC)
    
    time.sleep(.05)
    serial.send_preference(ROBOT_MAC, DataType_Boolean, "zEn", True)
    serial.send_preference(ROBOT_MAC, DataType_Boolean, "rollEn", False)
    serial.send_preference(ROBOT_MAC, DataType_Boolean, "rotateEn", False)
    serial.send_preference(ROBOT_MAC, DataType_Boolean, "pitchEn", True)
    serial.send_preference(ROBOT_MAC, DataType_Boolean, "yawEn", True)

    
    # // PID terms
    serial.send_preference(ROBOT_MAC, DataType_Float, "kpyaw", 2) #2
    serial.send_preference(ROBOT_MAC, DataType_Float, "kppyaw", 0.05) #2
    serial.send_preference(ROBOT_MAC, DataType_Float, "kdyaw", 0.05)#.1
    serial.send_preference(ROBOT_MAC, DataType_Float, "kddyaw", 0.05)#.1
    serial.send_preference(ROBOT_MAC, DataType_Float, "kiyaw", 0)
    serial.send_preference(ROBOT_MAC, DataType_Float, "kiyawrate", 0)

    serial.send_preference(ROBOT_MAC, DataType_Float, "yawrate_gamma", 0.5)
    serial.send_preference(ROBOT_MAC, DataType_Float, "rollrate_gamma", 0.85)
    serial.send_preference(ROBOT_MAC, DataType_Float, "pitchrate_gamma", 0.7)
    

    serial.send_preference(ROBOT_MAC, DataType_Float, "kpz", 0.3)
    serial.send_preference(ROBOT_MAC, DataType_Float, "kdz", 0.6)
    serial.send_preference(ROBOT_MAC, DataType_Float, "kiz", 0.0)

    serial.send_preference(ROBOT_MAC, DataType_Float, "kproll", 0)
    serial.send_preference(ROBOT_MAC, DataType_Float, "kdroll", 0)
    serial.send_preference(ROBOT_MAC, DataType_Float, "kppitch", 0)
    serial.send_preference(ROBOT_MAC, DataType_Float, "kdpitch", 0)

    # // Range terms for the integrals
    serial.send_preference(ROBOT_MAC, DataType_Float, "z_int_low", 0.0)
    serial.send_preference(ROBOT_MAC, DataType_Float, "z_int_high", 0.15)
    serial.send_preference(ROBOT_MAC, DataType_Float, "yawRateIntRange", 0)

    # // radius of the blimp
    serial.send_preference(ROBOT_MAC, DataType_Float, "lx", 0.7)

    serial.send_preference(ROBOT_MAC, DataType_Float, "servoRange", 260) #degrees
    serial.send_preference(ROBOT_MAC, DataType_Float, "servoBeta", 90) #degrees
    serial.send_preference(ROBOT_MAC, DataType_Float, "servo_move_min",0) #degrees

    serial.send_preference(ROBOT_MAC, DataType_Float, "botZlim", -1)
    serial.send_preference(ROBOT_MAC, DataType_Float, "pitchOffset", 0) #degrees
    serial.send_preference(ROBOT_MAC, DataType_Float, "pitchInvert", -1) #degrees



    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Boolean, "zEn", False)
    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Boolean, "rollEn", False)
    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Boolean, "rotateEn", False)
    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Boolean, "pitchEn", False)
    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Boolean, "yawEn", True)

    
    # // PID terms
    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Float, "kpyaw", 0) #2
    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Float, "kppyaw", 0) #2
    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Float, "kdyaw", 0)#.1
    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Float, "kddyaw", 0.2)#.1
    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Float, "kiyaw", 0)
    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Float, "kiyawrate", 0)

    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Float, "yawrate_gamma", 0.5)
    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Float, "rollrate_gamma", 0.85)
    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Float, "pitchrate_gamma", 0.7)
    

    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Float, "kpz", 0.3)
    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Float, "kdz", 0.6)
    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Float, "kiz", 0.0)

    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Float, "kproll", 0)
    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Float, "kdroll", 0)
    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Float, "kppitch", 0)
    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Float, "kdpitch", 0)

    # // Range terms for the integrals
    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Float, "z_int_low", 0.0)
    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Float, "z_int_high", 0.15)
    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Float, "yawRateIntRange", 0)

    # // radius of the blimp
    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Float, "lx", 0.7)

    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Float, "servoRange", 260) #degrees
    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Float, "servoBeta", 90) #degrees
    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Float, "servo_move_min",0) #degrees

    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Float, "botZlim", -1)
    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Float, "pitchOffset", 0) #degrees
    serial.send_preference(PASSIVE_ROBOT_MAC, DataType_Float, "pitchInvert", -1) #degrees
    serial.send_control_params(PASSIVE_ROBOT_MAC, (0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 1, 0))
    time.sleep(.2)

    # Joystick
    joystick = JoystickManager()
    mygui = SimpleGUI()
    niclaGUI = NiclaBox(max_x=240, max_y=160, x=120, y=80, width=120, height=80)
    
    sensors = serial.getSensorData()
    height = 0
    tz = 0
    if (sensors) :
        tz = sensors[1]
        height = sensors[0]
    ready = 0
    old_a = 0
    old_b = 0
    old_x = 0
    fx_ave = 0
    dt = .2
    fz2 = .2
    fx2 = .3
    servos = 75
    
    try:
        while True:
            # Axis input: [left_vert, left_horz, right_vert, right_horz, left_trigger, right_trigger]
            # Button inputs: [A, B, X, Y]
            axis, buttons = joystick.getJoystickInputs()
            
            if buttons[3] == 1: # y stops the program
                break
            if buttons[1] == 1 and old_b == 0: # b pauses the control
                if (sensors) :
                    tz = sensors[1]
                    height = sensors[0]
                if ready != 0:
                    ready = 0
                else:
                    ready = 1
            if buttons[2] == 1 and old_x == 0:
                if fz2 <= 0:
                    fz2 = -.4
                    fx2 = .3
                else:
                    fz2 = 0.2
                    fx2 = .3
            # if buttons[0] == 1 and old_a == 0:
            #     ready = 2
            old_x = buttons[2]
            old_b = buttons[1]
            old_a = buttons[0]
            if PRINT_JOYSTICK:
                print(" ".join(["{:.1f}".format(num) for num in axis]), buttons)

            #### CONTROL INPUTS to the robot here #########
            #height controller
            if abs(axis[0]) < .15:
                axis[0] = 0
            height += -axis[0] * dt 
            if height > 15:
                height = 15
            elif height < -5:
                height = -5
            fz = height
                
            if abs(axis[3]) < .15:
                axis[3] = 0
            fz2 += -axis[3] * dt 
            if fz2 > 1:
                fz2 = 1
            elif fz2 < -1:
                fz2 = -1
                
            # roll controller
            # if abs(axis[1]) < .15:
            #     axis[1] = 0
            # tx = axis[1] * .2
            tx = 0

            # yaw controller
            if abs(axis[4]) < .15:
                axis[4] = 0
            tz += -axis[4] *0.6 * dt
            # tz = -axis[4] * .1
            
            # fx speed controller
            fx = - axis[2] + axis[5]
            fx = fx * .5
            fx_ave = fx_ave * .8 + fx * .2 # smooths the fx for more gradual effects
            
            #print(tz, ":", height)
            #print(height)
            
            led = -buttons[2]
            ############# End CONTROL INPUTS ###############
            sensors = serial.getSensorData()
            # print(sensors)
            if (sensors):
                if (sensors[2] < 300):
                    niclaGUI.update(x=sensors[2], y=sensors[3], width=sensors[4], height=sensors[5])
                mygui.update(
                    cur_yaw=sensors[1],
                    des_yaw=tz,
                    cur_height=sensors[0],
                    des_height=height,
                    battery=0,#sensors[2],
                    distance=0,
                    connection_status=True,
                )
                
            # Send through serial port
            serial.send_control_params(ROBOT_MAC, (ready, fx_ave + .4, fz, 0, tz, led, 1, 0, 0, 0, 0, 0, 0))
            time.sleep(dt/2)
            serial.send_control_params(PASSIVE_ROBOT_MAC, (ready, .4, fz2, 0, 0, led, 0, 0, 0, 0, 0, 0, 0))
            time.sleep(dt/2)
            
    except KeyboardInterrupt:
        print("Stopping!")
        # Send zero input
serial.send_control_params(ROBOT_MAC, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
time.sleep(dt/2)
serial.send_control_params(PASSIVE_ROBOT_MAC, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
