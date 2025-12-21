from comm.Serial import SerialController
from gui.simpleGUI import SimpleGUI
from user_parameters import ROBOT_MACS,  SERIAL_PORT
import time

CALIBRATE = False
PRINT_JOYSTICK = True

"""Class that takes in input and sends it to the correct agent in the swarm

"""
class RobotMaster:
    def __init__(self, dt=0.3):
        self.serial = None
        self.robots = None # The list of robots
        self.ready = None
        self.mapping = {}

        self.current_robot_index = -1
        self.height, self.tz = 0.0, 0.0

        self.numSensors = 13

        self.dt = dt

    def setup(self, robots, camera="nicla", serial=SERIAL_PORT):
        self.robots = robots
        self.ready = [0 for _ in range(len(robots))]
        self.serial = SerialController(serial, timeout=0.5)
        self.mygui = SimpleGUI(camera)
        for robot_mac in self.robots:
            self.serial.manage_peer("A", robot_mac)
            self.serial.manage_peer("G", robot_mac)
            self.serial.send_control_params(robot_mac, (0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 1, 0))
            time.sleep(0.05)
        
    
    def get_last_n_keys(self, num_keys=1):
        return self.mygui.get_last_n_keys(num_keys)

    def updateGui(self, height=0.0, tz=0.0, printValues=False):
        
        sensors = None
        if self.current_robot_index != -1:
            sensors = self.serial.getSensorData()

        if sensors is None:
            sensors = [0] * self.numSensors
            self.mygui.update(cur_yaw=sensors[1], des_yaw=tz, cur_height=sensors[0], des_height=height,
                        battery=sensors[5], distance=0, connection_status=True)
        else:
            self.mygui.update(x=sensors[2], y=sensors[3], width=sensors[4], height=sensors[4], cur_yaw=sensors[1], des_yaw=tz, cur_height=sensors[0], des_height=height,
                        battery=sensors[5], distance=0, connection_status=True)
            
        if printValues:
            s = ''
            for senses in sensors:
                s += str(senses) + ' '
            print(s)
                
    def switchRobot(self, index):
        if 0 <= index <= len(self.robots):
            if self.current_robot_index == index-1:
                print("Already set to that robot.")
            elif self.current_robot_index != -1:
                sensors = self.serial.getSensorData()
                if sensors is None:
                    sensors = [0] * self.numSensors
                currRobot = self.robots[self.current_robot_index]
                currState = self.ready[self.current_robot_index]
                self.serial.send_control_params(currRobot, (5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                self.serial.send_control_params(currRobot, (currState, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                self.current_robot_index = index-1
                if self.current_robot_index != -1:
                    currRobot = self.robots[self.current_robot_index]
                    self.serial.send_control_params(currRobot, (5, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0))
                print("Switching to robot: ", index)
            else:
                self.current_robot_index = index-1
                currRobot = self.robots[self.current_robot_index]
                self.serial.send_control_params(currRobot, (5, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0))
                print("Switching to robot: ", index)
        else:
            print("Robot index out of range.")
    

    
    def processManual(self, axis, buttons, print_vals=False):
        if self.current_robot_index == -1:
            self.updateGui()
            return
        
        sensors = self.serial.getSensorData()

        # Button press logic
        if buttons[3]:  # Y puts into goal mode
            self.ready[self.current_robot_index] = 4 #if ready != 3 else 4
        if buttons[1]:  # B toggles pause
            self.ready[self.current_robot_index] = 0 if self.ready[self.current_robot_index] else 1
            if sensors:
                self.height, self.tz = (sensors[0], sensors[1])
        if buttons[2]:  # X puts into ball mode
            self.ready[self.current_robot_index] = 3
        if buttons[0]:  # A sets specific ready state
            self.ready[self.current_robot_index] = 2

        # Update old button states
        self.buttons = buttons[:]

        fz = -axis[0] * self.dt if abs(axis[0]) >= 0.15 else 0
        tz = -axis[4] * self.dt if abs(axis[4]) >= 0.15 else 0
        fx_ave = (-axis[2] + axis[5])

        # send control parameters
        
        currRobot = self.robots[self.current_robot_index]
        currState = self.ready[self.current_robot_index]
        self.updateGui(self.height, self.tz, print_vals)


        self.serial.send_control_params(currRobot, (currState, fx_ave, fz, 0, tz, buttons[5]-buttons[4], 1, 0, 0, 0, 0, 0, 0))


    def functionFactory(self, c, func, verbose=""):
        self.mapping[c] = (func, verbose)

    def runFunction(self, c, index=-1, *args):
        if c not in self.mapping:
            print("Function not mapped.")
            return
        func, verbose = self.mapping[c]
        index -= 1
        if index >= len(self.robots):
            print("Index out of range")
            return
        
        if index <= -1:
            print(verbose, ":",  "ff:ff:ff:ff:ff:ff")
            newState = func(self.serial, "ff:ff:ff:ff:ff:ff", args)
            if newState != -1:
                self.ready = [newState for _ in self.ready]
                self.current_robot_index = -1
            else:
                for ind in range(len(self.robots)):
                    self.serial.send_control_params(self.robots[ind], (self.ready[ind],0,0,0, 0, 0, 0, 0, 0, 0, 0, 1, 0))
        else:
            robot = self.robots[index]
            print(verbose, ":", index+1, "-", robot, ":", args)
            newState = func(self.serial, robot, args)
            if newState != -1:
                self.ready[index] = newState
            else:
                self.serial.send_control_params(self.robots[index], (self.ready[index],0,0,0, 0, 0, 0, 0, 0, 0, 0, 1, 0))

def stopOne(serial, robot):
    serial.send_control_params(robot, (5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    time.sleep(.05)
    serial.send_control_params(robot, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    time.sleep(.05)
    return 0

def main():
    try:
        robot_master = RobotMaster(0.3)
        robot_master.setup(ROBOT_MACS, "nicla")
        robot_master.functionFactory('s', stopOne, "Stop")
        index = "0"
      
        key_pressed = 's'
        
        if key_pressed == 'enter':
            i = int(index)
            robot_master.switchRobot(i)
            index = "0"
        elif len(key_pressed) == 1 and 32 <= ord(key_pressed) <= 127:
            if '0' <= key_pressed <= '9':
                index += key_pressed
            elif key_pressed == 'd':
                index = "0"
                print("Cleared index")
            else:
                i = int(index)
                robot_master.runFunction(key_pressed, i)
                index = "0"
        else:
            print("Invalid button.")
    except KeyboardInterrupt:
        print("Stopping!")
        return
    except Exception as e:
        print(e)
        return
    finally:
        robot_master.runFunction('s')
    

if __name__ == "__main__":
    main()