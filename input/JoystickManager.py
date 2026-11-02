
import pygame, time, sys
import numpy as np

# Raw axis numbers of an Xbox controller differ by OS (pygame 2 / SDL2). Linux (xpad), checked
# with XboxInputTest.py: LX 0, LY 1, LT 2, RX 3, RY 4, RT 5. Windows (XInput): LX 0, LY 1,
# RX 2, RY 3, LT 4, RT 5. With the Linux numbers on Windows, "LT" reads the right stick's
# horizontal axis, which rests at 0 and becomes a steady half backward command.
AXES = (dict(left_horz=0, left_vert=1, right_horz=2, right_vert=3, left_trigger=4, right_trigger=5)
        if sys.platform == 'win32' else
        dict(left_horz=0, left_vert=1, left_trigger=2, right_horz=3, right_vert=4, right_trigger=5))

class JoystickManager:
    def __init__(self, joystick_num=0):

        # Initialize Pygame for joystick handling
        pygame.init()
        pygame.joystick.init()  # Initialize the Joystick subsystem

        # Assuming there's at least one joystick connected
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(joystick_num)  # Initialize the first joystick
            self.joystick.init()
        else:
            print("No joystick detected!")
            self.joystick = None
            exit(1)
    
    def updateJoy(self):
        pygame.event.pump()  # Process event queue for the joystick
        # time.sleep(.1)  # TODO: is it necesary?

    def getJoysticks(self):
        if self.joystick:
            right_vert = self.joystick.get_axis(AXES['right_vert'])  # Right joystick vertical
            right_horz = self.joystick.get_axis(AXES['right_horz'])  # Right joystick horizontal
            left_vert = self.joystick.get_axis(AXES['left_vert'])  # Left joystick vertical
            left_horz = self.joystick.get_axis(AXES['left_horz'])  # Left joystick horizontal
            right_trigger = self.joystick.get_axis(AXES['right_trigger'])  # Right trigger
            left_trigger = self.joystick.get_axis(AXES['left_trigger'])  # Left trigger
            return [left_vert, left_horz, right_vert, right_horz, left_trigger, right_trigger]
        else:
            return [0, 0, 0, 0, 0, 0]

    def getButtons(self):
        if self.joystick:
            # Example button mapping (adjust based on your joystick)
            a = self.joystick.get_button(0)
            b = self.joystick.get_button(1)
            x = self.joystick.get_button(2)
            y = self.joystick.get_button(3)
            l_bumper = self.joystick.get_button(4)
            r_bumper = self.joystick.get_button(5)
            return [a, b, x, y, l_bumper, r_bumper]
        else:
            return [0, 0, 0, 0, 0, 0]


    def getJoystickInputs(self):
        self.updateJoy()
        return self.getJoysticks(), self.getButtons()



if __name__ == "__main__":


    joystick = JoystickManager()

    try:
        while True:
            axis, buttons = joystick.getJoystickInputs()
            # Print the output
            print(" ".join(["{:.1f}".format(num) for num in axis]), buttons)
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("Stopping!")