import pygame
from comm.Serial import SerialController
from input.JoystickManager import JoystickManager
from gui.simpleGUI import SimpleGUI
from gui.niclaGUI import NiclaBox
import time
from user_parameters import ROBOT_MACS,  SERIAL_PORT, PRINT_JOYSTICK, PUMP_MAC
ROBOT_MAC = None

def main():
    serial = SerialController(SERIAL_PORT, timeout=0.5)
    if serial.serial is None:
        return
    joystick = JoystickManager()
    mygui = SimpleGUI()
    niclaGUI = NiclaBox(max_x=240, max_y=160, x=120, y=80, width=120, height=80)
    pygame.init()
    # Get all Robot Mac addresses
    robots = ROBOT_MACS
    current_robot_index = -1
    ROBOT_MAC = "00:00:00:00:00:00"#robots[current_robot_index]


    # Setup communication with robot
    for robot_mac in robots:
        serial.manage_peer("A", robot_mac)
        time.sleep(0.05)
    # Setup communication with pump
    serial.manage_peer("A", PUMP_MAC)
    
    sensors = serial.getSensorData()
    # Initialize control variables
    height, tz =  (0, 0)
    ready = [0] * len(robots)
    old_buttons = [0] * 4  # A, B, X, Y
    fx_ave = 0
    dt = 0.3
    pump = False
    

    try:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN: # If a keyboard button is pressed
                    if event.key == pygame.K_PERIOD:
                        print("Pump On")
                        serial.send_control_params(PUMP_MAC, (1, 0, 0, 0, 0, 250, 0, 0, 0, 0, 0, 0, 0))
                    elif event.key == pygame.K_COMMA:
                        print("Pump Off")
                        serial.send_control_params(PUMP_MAC, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                    elif event.key == pygame.K_m:
                        serial.send_control_params(robots[4], (1, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                    elif event.key == pygame.K_k:
                        serial.send_control_params(robots[2], (1, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))

                    # QWERTY row for setting flag 2
                    elif event.key == pygame.K_q: # Flag 2 to blimp 0
                        serial.send_control_params(robots[0], (3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                        time.sleep(.1)
                        serial.send_control_params(robots[0], (2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                    elif event.key == pygame.K_w: # Flag 2 to blimp 1
                        serial.send_control_params(robots[1], (3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                        time.sleep(.1)
                        serial.send_control_params(robots[1], (2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                    elif event.key == pygame.K_e: # Flag 2 to blimp 2
                        serial.send_control_params(robots[2], (3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                        time.sleep(.1)
                        serial.send_control_params(robots[2], (2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                    elif event.key == pygame.K_r: # Flag 2 to blimp 3
                        serial.send_control_params(robots[3], (3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                        time.sleep(.1)
                        serial.send_control_params(robots[3], (2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                    elif event.key == pygame.K_t: # Flag 2 to blimp 4
                        serial.send_control_params(robots[4], (3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                        time.sleep(.1)
                        serial.send_control_params(robots[4], (2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                    elif event.key == pygame.K_y: # Flag 2 to blimp 5
                        serial.send_control_params(robots[5], (3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                        time.sleep(.1)
                        serial.send_control_params(robots[5], (2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))

                    # ASDFGH row for setting flag 0
                    elif event.key == pygame.K_a: # Flag 3 to blimp 0
                        serial.send_control_params(robots[0], (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                    elif event.key == pygame.K_s: # Flag 3 to blimp 1
                        serial.send_control_params(robots[1], (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                    elif event.key == pygame.K_d: # Flag 3 to blimp 2
                        serial.send_control_params(robots[2], (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                    elif event.key == pygame.K_f: # Flag 3 to blimp 3
                        serial.send_control_params(robots[3], (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                    elif event.key == pygame.K_g: # Flag 3 to blimp 4
                        serial.send_control_params(robots[4], (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                    elif event.key == pygame.K_h: # Flag 3 to blimp 5
                        serial.send_control_params(robots[5], (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))

                    # ZXCVB row for setting flag 4
                    elif event.key == pygame.K_z: # Flag 4 to blimp 0
                        serial.send_control_params(robots[0], (4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                    elif event.key == pygame.K_x: # Flag 4 to blimp 1
                        serial.send_control_params(robots[1], (4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                    elif event.key == pygame.K_c: # Flag 4 to blimp 2
                        serial.send_control_params(robots[2], (4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                    elif event.key == pygame.K_v: # Flag 4 to blimp 3
                        serial.send_control_params(robots[3], (4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                    elif event.key == pygame.K_b: # Flag 4 to blimp 4
                        serial.send_control_params(robots[4], (4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))

                    if event.key == pygame.K_SPACE:
                        for robot_mac in robots:
                            serial.send_control_params(robot_mac, (3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                            time.sleep(.2)
                            serial.send_control_params(robot_mac, (2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                            time.sleep(.1)
                        ready[current_robot_index] = 2
                    elif event.key == pygame.K_p:
                        count = 0
                        for robot_mac in robots:
                            ready[count] = 0
                            count += 1
                            serial.send_control_params(robot_mac, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                            time.sleep(.1)
                        ready[current_robot_index] = 0
                        
                    elif event.key == pygame.K_o:
                        
                        for robot_mac in robots[:-2]:
                            serial.send_control_params(robot_mac, (4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                            time.sleep(.1)
                            
                    elif event.key == pygame.K_i:
                        count = 0
                        for robot_mac in robots:
                            ready[count] = 3
                            count+=1
                            serial.send_control_params(robot_mac, (3, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                            time.sleep(.1)
                    elif event.key == pygame.K_u:
                        for robot_mac in robots[:-2]:
                            serial.send_control_params(robot_mac, (2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                            time.sleep(.1)       
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                    elif pygame.K_0 <= event.key <= pygame.K_9:
                        index = event.key - pygame.K_0 - 1
                        if 0 <= index < len(robots):
                            if current_robot_index == index:
                                print("Already set to that robot.")
                            else:
                                serial.send_control_params(ROBOT_MAC, (5, fx_ave, height, 0, tz, 0, 0, 0, 0, 0, 0, 0, 0))
                                serial.send_control_params(ROBOT_MAC, (ready[current_robot_index], fx_ave, height, 0, tz, 0, 0, 0, 0, 0, 0, 0, 0))
                                current_robot_index = index
                                ROBOT_MAC = robots[current_robot_index]
                                serial.send_control_params(ROBOT_MAC, (5, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0))
                                time.sleep(0.1)
                                sensors = serial.getSensorData()
                                if sensors is None:
                                    height, tz = 0, 0
                                else:
                                    height, tz = (sensors[0], sensors[1])
                                
                                print(f"Switched to robot {ROBOT_MAC}")
                        else:
                            serial.send_control_params(ROBOT_MAC, (5, fx_ave, height, 0, tz, 0, 0, 0, 0, 0, 0, 0, 0))
                            current_robot_index = index
                            ROBOT_MAC = "00:00:00:00:00:00"
            axis, buttons = joystick.getJoystickInputs()

            sensors = serial.getSensorData()
            if sensors:
                s = ''
                for senses in sensors:
                    s += str(senses) + ' '
                print(s)
                if sensors[2] < 300:
                    niclaGUI.update(x=sensors[2], y=sensors[3], width=sensors[4], height=sensors[4])
                mygui.update(cur_yaw=sensors[1], des_yaw=tz, cur_height=sensors[0], des_height=height,
                             battery=sensors[5], distance=0, connection_status=True)
            
            # Button press logic
            if buttons[3] and not old_buttons[3]:  # Y puts into goal mode
                ready[current_robot_index] = 4 #if ready != 3 else 4
            if buttons[1] and not old_buttons[1]:  # B toggles pause
                ready[current_robot_index] = 0 if ready[current_robot_index] else 1
                if sensors:
                    height, tz = (sensors[0], sensors[1])
            if buttons[2] and not old_buttons[2]:  # X puts into ball mode
                ready[current_robot_index] = 3
                height, tz = (sensors[0], sensors[1])
            if buttons[0] and not old_buttons[0]:  # A sets specific ready state
                ready[current_robot_index] = 2

            # Update old button states
            old_buttons = buttons[:]
            
            # Display joystick values if enabled
            if PRINT_JOYSTICK:
                print(" ".join(["{:.1f}".format(num) for num in axis]), buttons)

            if ready[current_robot_index] != 5:
                # Control inputs to the robot
                height += -axis[0] * dt if abs(axis[0]) >= 0.15 else 0
                height = max(min(height, 15), -10)
                tz += -axis[4] * 1.2 * dt if abs(axis[4]) >= 0.15 else 0
            else:
                # Control inputs to the robot
                height = -axis[0] * .5 * dt if abs(axis[0]) >= 0.15 else 0
                tz = -axis[4] * .5 * dt if abs(axis[4]) >= 0.15 else 0
            fx_ave = (-axis[2] + axis[5]) * 0.65
            # fx_ave = fx_ave * 0.67 + fx * 0.33

            # send control parameters
            serial.send_control_params(ROBOT_MAC, (ready[current_robot_index], fx_ave, height, 0, tz, -buttons[2], 1, 0, 0, 0, 0, 0, 0))
            
            time.sleep(dt)
    except KeyboardInterrupt:
        print("Stopping!")
    finally:
        serial.send_control_params(ROBOT_MAC, (5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        for robot_mac in robots:
            serial.send_control_params(robot_mac, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
            time.sleep(0.05)
        serial.send_control_params(PUMP_MAC, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        time.sleep(0.05)

if __name__ == "__main__":
    main()
