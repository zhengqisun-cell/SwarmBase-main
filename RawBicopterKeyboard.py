
from comm.Serial import SerialController, DataType_Int, DataType_Float
# Make sure to import KeyboardManager from its location in your project
from input.KeyboardManager import KeyboardManager
from gui.simpleGUI import SimpleGUI
from user_parameters import ROBOT_MACS, SERIAL_PORT, PRINT_JOYSTICK
import time

ROBOT_MAC = ROBOT_MACS[0]



if __name__ == "__main__":
    # Communication
    serial = SerialController(SERIAL_PORT, timeout=.1)  # 5-second timeout
    serial.manage_peer("A", ROBOT_MAC)
    serial.manage_peer("G", ROBOT_MAC)
    serial.send_preference(ROBOT_MAC, DataType_Float, "kpz", .6)
    serial.send_preference(ROBOT_MAC, DataType_Float, "kdz", .8)
    serial.send_control_params(ROBOT_MAC, (0,0,90,90, 0, 0, 0, 0, 0, 0, 0, 1, 0)) #refresh parameters
    time.sleep(.2)

    # Keyboard
    keyboard = KeyboardManager()
    sensorGUI = SimpleGUI()

    try:
        while True:
            # Axis input: [ws, ad, V^, <>, q, e] (these duo letters represent a "joystick" axis equivalent)
            # Button inputs: [Z, X, C, V] mapped to [A, B, X, Y]
            axis, buttons = keyboard.getKeyboardInputs()

            if PRINT_JOYSTICK:
                print("Axis:", " ".join(["{:.1f}".format(num) for num in axis]), "Buttons:", buttons)

            #### CONTROL INPUTS to the robot here #########
            # Example control inputs (modify as necessary for your application)
            throttle = (axis[0] + 1) / 2.0 

            m1 = throttle  # Motor 1: a value between 0-1
            m2 = throttle  # Motor 2: a value between 0-1
            s1 = 90.  # Servo 1: a value between 0-180
            s2 = 90.  # Servo 2: a value between 0-180
            led = axis[0]  # Example: press W in the keyboard to control an LED

            ############# End CONTROL INPUTS ###############
            sensors = serial.getSensorData()

            if sensors:
                print(sensors)
                sensorGUI.update(
                    cur_yaw=0,
                    des_yaw=-0,
                    cur_height=sensors[0],
                    des_height=0,
                    battery=0,
                    distance=0,
                    connection_status=True,
                )
            else:
                print("No sensors")
            # Send through serial port
            serial.send_control_params(ROBOT_MAC, (m1, m2, s1, s2, led, 0, 0, 0, 0, 0, 0, 0, 0))
            time.sleep(.02)
            
    except KeyboardInterrupt:
        print("Stopping!")
        # Send zero input
    serial.send_control_params(ROBOT_MAC, (0, 0, 180, 180, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    serial.close()
