"""
Author       : Hanqing Qi
Date         : 2023-11-11 14:47:43
LastEditors  : Hanqing Qi
LastEditTime : 2023-11-12 16:30:56
FilePath     : /GUI/SimpleGUI_V3/simpleGUI.py
Description  : The GUI for bicopter control V3
"""

import matplotlib.pyplot as plt
from gui.simpleGUIutils import *
from collections import deque



class SimpleGUI:
    def on_key_press(self, event):
        if event.key == 'ctrl+c':
            exit(1)
        self.keystrokes.append(event.key)

    def __init__(self, camera="nicla", n=2):
        # Plotting initialization
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=GS)
        self.ax.set_facecolor(C["k"])  # Set background color
        self.fig.patch.set_facecolor(C["k"])  # Set background color
        self.ax.set_xlim(0, GS[0])
        self.ax.set_ylim(0, GS[1])
        self.ax.set_aspect("equal", "datalim")  # Set aspect ratio
        self.ax.set_xticks([])  # Remove x ticks
        self.ax.set_yticks([])  # Remove y ticks
        self.ax.axis("off")  # Remove axis
        self.keystrokes = deque(maxlen=n)
        for key in plt.rcParams.keys():
            if key.startswith("keymap."):
                plt.rcParams[key] = []

        # plt.rcParams['keymap.quit'] = ['ctrl+c']  # Keep Ctrl+C to quit        
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)

        init_nicla(self, camera)
        init_yaw(self)
        init_height(self)
        init_variables(self)
        init_battery(self)
        init_distance(self)
        init_connection_status(self)

    def update(self, x: float = 0, y: float = 0, width: float = 0, height: float = 0, cur_yaw: float = 0, des_yaw: float = 0, cur_height: float = 0, des_height: float = 0, battery: float = 0, distance: float = 0, connection_status: bool = False):
        update_nicla(self, x, y, width, height)
        update_yaw(self, cur_yaw, des_yaw)
        update_height(self, cur_height, des_height)
        update_battery(self, battery)
        update_distance(self, distance)
        update_connection_status(self, connection_status)
        plt.draw()
        plt.pause(0.001)

    def get_last_n_keys(self, num_keys=1):
        """Get and pop the last `num_keys` keystrokes."""
        num_keys = min(num_keys, len(self.keystrokes))  # Limit to available keys
        last_keys = [self.keystrokes.popleft() for _ in range(num_keys)]
        return last_keys

if __name__ == "__main__":
    mygui = SimpleGUI("openmv")
    import math
    # Change width and height in a loop to see updates
    width, height = 100, 60
    increasing = True        
    for i in range(101):
        # Animate the rectangle's size
        if increasing:
            width += 1
            height += 1
            if width > 140:
                increasing = False
        else:
            width -= 1
            height -= 1
            if width < 80:
                increasing = True
        
        # Update the rectangle with new dimensions
        mygui.update(
            x = 200,
            y= 130,
            width = width,
            height = height,
            cur_yaw=math.pi * i / 100,
            des_yaw=- math.pi * i / 100,
            cur_height=15 * i / 100,
            des_height=15 * (1 - i / 100),
            battery=4.5 * i / 100,
            distance=400 * i / 100,
            connection_status=True,
        )
        plt.pause(0.05)
    plt.ioff()
    plt.show()
