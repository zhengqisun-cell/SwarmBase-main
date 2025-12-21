from comm.Serial import SerialController, DataType_Int, DataType_Float, DataType_Boolean
from input.JoystickManager import JoystickManager
from gui.simpleGUI import SimpleGUI
from gui.niclaGUI import NiclaBox
import time
from user_parameters import ROBOT_MAC, SERIAL_PORT, PRINT_JOYSTICK

def main():
    serial = SerialController(SERIAL_PORT, timeout=0.5)
    joystick = JoystickManager()
    mygui = SimpleGUI()
    niclaGUI = NiclaBox(max_x=240, max_y=160, x=120, y=80, width=120, height=80)
    
    # Setup communication with robot
    
    serial.manage_peer("A", ROBOT_MAC)
    time.sleep(0.05)

    # Initialize control variables
    sensors = serial.getSensorData()
    height, tz = (sensors[0], sensors[1]) if sensors else (0, 0)
    ready = 0
    old_buttons = [0] * 4  # A, B, X, Y
    fx_ave = 0
    dt = 0.1

    try:
        while True:
            axis, buttons = joystick.getJoystickInputs()
            
            # Button press logic
            if buttons[3]:  # Y stops the program
                break
            if buttons[1] and not old_buttons[1]:  # B toggles pause
                ready = 0 if ready else 1
            if buttons[2] and not old_buttons[2]:  # X toggles special mode
                ready = 3 if ready != 3 else 4
            if buttons[0] and not old_buttons[0]:  # A sets specific ready state
                ready = 2

            # Update old button states
            old_buttons = buttons[:]
            
            # Display joystick values if enabled
            if PRINT_JOYSTICK:
                print(" ".join(["{:.1f}".format(num) for num in axis]), buttons)

            # Control inputs to the robot
            height += -axis[0] * dt if abs(axis[0]) >= 0.15 else 0
            height = max(min(height, 15), -3)
            tz += -axis[4] * 1.2 * dt if abs(axis[4]) >= 0.15 else 0
            fx = (-axis[2] + axis[5]) * 0.2
            fx_ave = fx_ave * 0.8 + fx * 0.2

            # Update GUI and send control parameters
            sensors = serial.getSensorData()
            if sensors:
                if sensors[2] < 300:
                    niclaGUI.update(x=sensors[2], y=sensors[3], width=sensors[4], height=sensors[4])
                mygui.update(cur_yaw=sensors[1], des_yaw=tz, cur_height=sensors[0], des_height=height, battery=sensors[5], distance=0, connection_status=True)
            serial.send_control_params(ROBOT_MAC, (ready, fx_ave, height, 0, tz, -buttons[2], 1, 0, 0, 0, 0, 0, 0))
            
            time.sleep(dt)
    except KeyboardInterrupt:
        print("Stopping!")
        serial.send_control_params(ROBOT_MAC, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))

if __name__ == "__main__":
    main()
