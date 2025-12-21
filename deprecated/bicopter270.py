

from comm.Serial import SerialController, DataType_Int, DataType_Float, DataType_Boolean
from input.JoystickManager import JoystickManager
from gui.simpleGUI import SimpleGUI
from gui.niclaGUI import NiclaBox
import time

##### Insert your robot's MAC ADDRESS here ####
## (you can get it by running your arduino and looking at the serial monitor for your flying drone) ##
ROBOT_MAC = "34:85:18:AC:0E:30"#"34:85:18:AB:FE:68" # "DC:54:75:D7:B3:E8"
PASSIVE_ROBOT_MAC = "48:27:E2:E6:E0:1C"#48:27:E2:E6:E0:1C
### Insert your SERIAL PORT here ###
## may look like "COM5" in windows or "/dev/tty.usbmodem14301" in mac  #
## look in arduino for the port that your specific transeiver is connected to  ##
## Note: make sure that your serial monitor is OFF in arduino or else you will get "access is denied" error. ##
PORT = "COM12"


# For debug purposes
PRINT_JOYSTICK = False


BaseStationAddress = "" # you do not need this, just make sure your DroneMacAddress is not your base station mac address

def sendParamsActive(serial, mac):
    serial.manage_peer("A", mac)
    time.sleep(.05)
    serial.send_preference(mac, DataType_Boolean, "zEn", True)
    serial.send_preference(mac, DataType_Boolean, "rollEn", False)
    serial.send_preference(mac, DataType_Boolean, "rotateEn", False)
    serial.send_preference(mac, DataType_Boolean, "pitchEn", True)
    serial.send_preference(mac, DataType_Boolean, "yawEn", True)


    # // PID terms
    serial.send_preference(mac, DataType_Float, "kpyaw", .8) #2
    serial.send_preference(mac, DataType_Float, "kdyaw", 1.1)#.1
    serial.send_preference(mac, DataType_Float, "kiyaw", 0)
    serial.send_preference(mac, DataType_Float, "kiyawrate", 0)

    serial.send_preference(mac, DataType_Float, "kpz", 0.3)
    serial.send_preference(mac, DataType_Float, "kdz", 0.6)
    serial.send_preference(mac, DataType_Float, "kiz", 0.1)
    serial.send_preference(mac, DataType_Float, "kproll", 0)
    serial.send_preference(mac, DataType_Float, "kdroll", 0)

    # // Range terms for the integrals

    serial.send_preference(mac, DataType_Float, "z_int_low", 0.05)
    serial.send_preference(mac, DataType_Float, "z_int_high", 0.15)
    serial.send_preference(mac, DataType_Float, "yawRateIntRange", 0)

    # // radius of the blimp
    serial.send_preference(mac, DataType_Float, "lx", 0.7)
    serial.send_preference(mac, DataType_Float, "servoRange", 260) #degrees
    serial.send_preference(mac, DataType_Float, "servoBeta", 90) #degrees
    serial.send_preference(mac, DataType_Float, "botZlim", -1)
    serial.send_preference(mac, DataType_Float, "pitchOffset", 0) #degrees
    serial.send_preference(mac, DataType_Float, "pitchInvert", -1) #degrees
    serial.send_control_params(mac, (0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 1, 0))
    time.sleep(.2)

def sendParamsPassive(serial, mac):
    serial.manage_peer("A", mac)
    time.sleep(.05)
    serial.send_preference(mac, DataType_Boolean, "zEn", False)
    serial.send_preference(mac, DataType_Boolean, "rollEn", False)
    serial.send_preference(mac, DataType_Boolean, "rotateEn", False)
    serial.send_preference(mac, DataType_Boolean, "pitchEn", False)
    serial.send_preference(mac, DataType_Boolean, "yawEn", False)


    # // PID terms
    serial.send_preference(mac, DataType_Float, "kpyaw", 1.5) #2
    serial.send_preference(mac, DataType_Float, "kdyaw", .1)#.1
    serial.send_preference(mac, DataType_Float, "kiyaw", 0)
    serial.send_preference(mac, DataType_Float, "kiyawrate", 0)

    serial.send_preference(mac, DataType_Float, "kpz", 0.3)
    serial.send_preference(mac, DataType_Float, "kdz", 0.6)
    serial.send_preference(mac, DataType_Float, "kiz", 0.1)
    serial.send_preference(mac, DataType_Float, "kproll", 0)
    serial.send_preference(mac, DataType_Float, "kdroll", 0)

    # // Range terms for the integrals

    serial.send_preference(mac, DataType_Float, "z_int_low", 0.05)
    serial.send_preference(mac, DataType_Float, "z_int_high", 0.15)
    serial.send_preference(mac, DataType_Float, "yawRateIntRange", 0)

    # // radius of the blimp
    serial.send_preference(mac, DataType_Float, "lx", 0.7)
    serial.send_preference(mac, DataType_Float, "servoRange", 180) #degrees
    serial.send_preference(mac, DataType_Float, "servoBeta", 45) #degrees
    serial.send_preference(mac, DataType_Float, "botZlim", -1)
    serial.send_preference(mac, DataType_Float, "pitchOffset", 0) #degrees
    serial.send_preference(mac, DataType_Float, "pitchInvert", -1) #degrees
    serial.send_control_params(mac, (0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 1, 0))
    time.sleep(.2)


if __name__ == "__main__":
    # Communication
    serial = SerialController(PORT, timeout=.5)  # 5-second timeout
    serial.manage_peer("G", ROBOT_MAC)
    sendParamsActive(serial, ROBOT_MAC)
    sendParamsPassive(serial, PASSIVE_ROBOT_MAC)

    sensors = serial.getSensorData()
    height = 0
    tz = 0
    if (sensors) :
        tz = sensors[1]
        height = sensors[0]
    # Joystick
    joystick = JoystickManager()
    mygui = SimpleGUI()
    niclaGUI = NiclaBox(max_x=240, max_y=160, x=120, y=80, width=120, height=80)
    ready = 0
    old_b = 0
    old_x = 0
    dt = .1
    servos = 75
    fz2 = 0
    fx2 = .3
    try:
        while True:
            # Axis input: [left_vert, left_horz, right_vert, right_horz, left_trigger, right_trigger]
            # Button inputs: [A, B, X, Y]
            axis, buttons = joystick.getJoystickInputs()

            if buttons[3] == 1: # y stops the program
                break
            if buttons[1] == 1 and old_b == 0: # b pauses the control
                if ready != 0:
                    ready = 0
                else:
                    ready = 1
            if buttons[2] == 1 and old_x == 0:
                if fz2 <= 0:
                    fz2 = -.4
                    fx2 = .5
                else:
                    fz2 = 0
                    fx2 = .3

            old_x = buttons[2]
            old_b = buttons[1]
            if PRINT_JOYSTICK:
                print(" ".join(["{:.1f}".format(num) for num in axis]), buttons)

            #### CONTROL INPUTS to the robot here #########
            if abs(axis[0]) < .15:
                axis[0] = 0
            height += -axis[0] * dt
            if height > 15:
                height = 15
            elif height < -5:
                height = -5
            # fz2 = -axis[0] * .4

            if abs(axis[1]) < .15:
                axis[1] = 0
            tx = axis[1] * .5

            if abs(axis[4]) < .15:
                axis[4] = 0
            tz += -axis[4] *2.2 * dt
            tz2 = -axis[4] * .1

            fx = axis[2] - axis[5]
            if (fx < 0):
                fx = fx * .3

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
            # fx = 0
            fz = height
            # tx = 0
            # tz = 0
            # Send through serial port
            serial.send_control_params(ROBOT_MAC, (ready, fx + .3, fz, tx, tz, led, 0, 0, 0, 0, 0, 0, 0))
            serial.send_control_params(PASSIVE_ROBOT_MAC, (ready, fx2, fz2, 0, 0, led, 0, 0, 0, 0, 0, 0, 0))
            time.sleep(dt)
            
    except KeyboardInterrupt:
        print("Stopping!")
        # Send zero input
serial.send_control_params(ROBOT_MAC, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
serial.send_control_params(PASSIVE_ROBOT_MAC, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
