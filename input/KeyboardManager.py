import pygame, time
import numpy as np

# Initialize Pygame
pygame.init()

class KeyboardManager:
    def __init__(self):
        pygame.init()  # Initialize Pygame
        self.screen = pygame.display.set_mode((640, 480))  # Required to capture events

    def updateKeys(self):
        pygame.event.pump()  # Process the event queue

    def getJoysticks(self):
        keys = pygame.key.get_pressed()
        # Map WASD to the left joystick
        left_vert = keys[pygame.K_s] - keys[pygame.K_w]
        left_horz = keys[pygame.K_d] - keys[pygame.K_a]
        # Map Arrow keys to the right joystick
        right_vert = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        right_horz = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        # Map Q and E to the triggers
        left_trigger = keys[pygame.K_q]
        right_trigger = keys[pygame.K_e]
        return [left_vert, left_horz, right_vert, right_horz, left_trigger, right_trigger]

    def getButtons(self):
        keys = pygame.key.get_pressed()
        # Map ZXCV to XYAB
        z = keys[pygame.K_z]
        x = keys[pygame.K_x]
        c = keys[pygame.K_c]
        v = keys[pygame.K_v]
        return [z, x, c, v]

    def getKeyboardInputs(self):
        self.updateKeys()
        return self.getJoysticks(), self.getButtons()

if __name__ == "__main__":
    keyboard = KeyboardManager()

    try:
        while True:
            axis, buttons = keyboard.getKeyboardInputs()
            # Print the output
            print("Axis:", " ".join(["{:.1f}".format(num) for num in axis]), "Buttons:", buttons)
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("Stopping!")
