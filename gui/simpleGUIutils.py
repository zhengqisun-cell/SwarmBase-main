"""
Author       : Hanqing Qi
Date         : 2023-11-11 14:47:43
LastEditors  : Hanqing Qi
LastEditTime : 2023-11-12 15:51:51
FilePath     : /GUI/SimpleGUI_V3/simpleGUIutils.py
Description  : Some functions for the simpleGUI V3  
"""

import matplotlib.widgets as widgets
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from gui.simpleGUIparams import *
import numpy as np

def init_nicla(self, board="nicla") -> None:
    if board == "nicla":
        self.NB = [240, 160]
    elif board == "openmv":
        self.NB = [320, 240]

    self.NBYR = self.NB[1] / self.NB[0]
    self.NBS = [0.4 * GS[0], max(0, min(0.4 * GS[0], self.NBYR * 0.4 * GS[0]))]
    self.NBP = [0.6 * GS[0], (0.5 - (self.NBS[1]/(2*GS[1]))) * GS[1]]

    self.nicla_max_x = self.NB[0]
    self.nicla_max_y = self.NB[1]
    self.nicla_x = self.NBP[0]
    self.nicla_y = self.NBP[1]
    self.nicla_width = self.NBS[0]
    self.nicla_height = self.NBS[1]
    self.nicla_color = C["p"]
    
    # Create the rectangle
    self.nicla_window = patches.Rectangle(
        (self.NBP[0], self.NBP[1]),  # Bottom-left corner
        self.NBS[0],
        self.NBS[1],
        linewidth=1,
        edgecolor='white',
        facecolor='none'  # Transparent filling
    )
    
    # Add the outer rectangle to the plot
    self.ax.add_patch(self.nicla_window)
    
    # Define the inner rectangle properties
    self.inner_rect = patches.Rectangle(
        (0, 0),  # Bottom-left corner of the inner rectangle
        0,  # Initial width
        0,  # Initial height
        edgecolor='none',
        facecolor=self.nicla_color  # Red filling
    )
    # Add the inner rectangle to the plot
    self.ax.add_patch(self.inner_rect)

    # # Set plot limits
    # self.ax.set_xlim(0, 6)
    # self.ax.set_ylim(0, 4)
    # self.ax.set_aspect('equal')
    # self.rect = patches.Rectangle((0 * GS[0], 0 * GS[1]),
    #                                 self.width, self.height,
    #                                 linewidth=1, edgecolor="black", facecolor=self.color)
    # self.ax.add_patch(self.rect)

def update_nicla(self, x=None, y=None, width=None, height=None):
    """Update the rectangle's position and size."""
    # Update the rectangle's position and size if new values are provided
    if x is None:
        return
    
    self.nicla_x = self.NBP[0] + ((x - width / 2) / self.NB[0]) * self.NBS[0]
    self.nicla_y = self.NBP[1] + ((y - height / 2) / self.NB[1]) * self.NBS[1]
    self.nicla_width = (width / self.NB[0]) * self.NBS[0]
    self.nicla_height = (height / self.NB[1]) * self.NBS[1]

    # # Ensure the rectangle stays within the specified boundaries
    self.nicla_x = max(self.NBP[0], min(self.nicla_x, self.NBP[0] + self.NBS[0]))
    self.nicla_y = max(self.NBP[1], min(self.nicla_y, self.NBP[1] + self.NBS[1]))
    self.nicla_width = min(self.nicla_width, self.NBP[0] + self.NBS[0] - self.nicla_x)
    self.nicla_height = min(self.nicla_height, self.NBP[1] + self.NBS[1] - self.nicla_y)

    # Update the rectangle's position and size
    self.inner_rect.set_xy((self.nicla_x, self.nicla_y))
    self.inner_rect.set_width(self.nicla_width)
    self.inner_rect.set_height(self.nicla_height)
    
# Initialize the yaw circle
def init_yaw(self) -> None:
    # Plot
    center_dot = self.ax.scatter(YC[0], YC[1], s=40, color=C["w"], zorder=3)
    self.ax.add_patch(patches.Circle(YC, YR, fill=False, color=C["w"], linewidth=LW, zorder=1))
    add_ticks_circle(self)
    self.current_yaw = self.ax.arrow(YC[0], YC[1], 0, 0.8 * YR, head_width=0.1 * YR, head_length=0.2 * YR, fc=C["b"], ec=C["b"], linewidth=LW, zorder=2)
    self.desired_yaw = self.ax.arrow(YC[0], YC[1], 0, 0.8 * YR, head_width=0.1 * YR, head_length=0.2 * YR, fc=C["r"], ec=C["r"], linewidth=LW, zorder=2)
    # Text
    self.ax.text(YC[0], YP[0], "Yaw", fontsize=FS, color=C["w"], ha="center", va="center")  # Yaw
    self.current_yaw_tx = self.ax.text(YC[0], (YS[1] - YOF[1]) * 1.1, "Current: 0˚", fontsize=FS, color=C["b"], ha="center", va="center")  # Current yaw text
    self.desired_yaw_tx = self.ax.text(YC[0], (YS[1] - YOF[1]) * 1.01, "Desired: 0˚", fontsize=FS, color=C["r"], ha="center", va="center")  # Desired yaw text
    # Value
    self.des_yaw = 0  # Desired yaw
    self.cur_yaw = 0  # Current yaw


# Update the yaw circle
def update_yaw(self, cur_yaw: float = 0, des_yaw: float = 0, slider: bool = True) -> None:
    x1, y1 = YR * 0.8 * np.cos(cur_yaw), YR * 0.8 * np.sin(cur_yaw)  # Current yaw arrow head coordinates
    x2, y2 = YR * 0.8 * np.cos(des_yaw), YR * 0.8 * np.sin(des_yaw)  # Desired yaw arrow head coordinates
    self.current_yaw.remove()  # Remove the old arrow
    self.desired_yaw.remove()  # Remove the old arrow
    self.current_yaw = self.ax.arrow(YC[0], YC[1], x1, y1, head_width=0.1 * YR, head_length=0.2 * YR, fc=C["b"], ec=C["b"], linewidth=LW, zorder=2)
    self.desired_yaw = self.ax.arrow(YC[0], YC[1], x2, y2, head_width=0.1 * YR, head_length=0.2 * YR, fc=C["r"], ec=C["r"], linewidth=LW, zorder=2)
    self.current_yaw_tx.set_text(f"Current: {np.degrees(cur_yaw):.2f}˚")  # Current yaw
    self.desired_yaw_tx.set_text(f"Desired: {np.degrees(des_yaw):.2f}˚")  # Desired yaw
    self.cur_yaw = np.degrees(cur_yaw)  # Current yaw
    self.des_yaw = np.degrees(des_yaw)  # Desired yaw
    # Update the slider value
    if slider:
        self.sliders[0].set_val(self.des_yaw)


# Add ticks to the circle
def add_ticks_circle(self) -> None:
    emphasized_angles = [0, 90, 180, 270]
    for angle in range(0, 360, 10):
        radian = np.radians(angle)
        start_x = YC[0] + YR * np.cos(radian)
        start_y = YC[1] + YR * np.sin(radian)
        if angle in emphasized_angles:
            end_x = YC[0] + (YR * 0.85) * np.cos(radian)
            end_y = YC[1] + (YR * 0.85) * np.sin(radian)
            self.ax.plot([start_x, end_x], [start_y, end_y], color=C["w"], linewidth=LW, zorder=1)
        else:
            end_x = YC[0] + (YR * 0.925) * np.cos(radian)
            end_y = YC[1] + (YR * 0.925) * np.sin(radian)
            self.ax.plot([start_x, end_x], [start_y, end_y], color=C["w"], linewidth=LW, zorder=1)


# Initialize the height bar
def init_height(self) -> None:
    # Plot the debug rectangle of the height bar
    # self.ax.add_patch(patches.Rectangle(HP, HS[0], HS[1], linewidth=0.5, edgecolor=C["w"], fill=False, zorder=1))
    cur_bar_center = HP[0] + HOF[0] + HW * 0.5
    des_bar_center = HP[0] + HOF[0] + HW * 1.5
    self.cur_height_bar = self.ax.bar(cur_bar_center, 0, HW, color=C["b"], bottom=HOF[1])
    add_ticks_bar(self, HP[0] + HOF[0])
    self.des_height_bar = self.ax.bar(des_bar_center, 0, HW, color=C["r"], bottom=HOF[1])
    add_ticks_bar(self, HP[0] + HOF[0] + HW)
    # Text
    self.ax.text(HP[0] + HOF[0] + HW, HP[1] + HS[1] + 0.01, "Height", fontsize=FS, color=C["w"], ha="center", va="center", zorder=1)  # Height
    self.ax.text(cur_bar_center, HP[1] - 0.01, "Cur", fontsize=FS, color=C["b"], ha="center", va="center")  # Current height
    self.ax.text(des_bar_center, HP[1] - 0.01, "Des", fontsize=FS, color=C["r"], ha="center", va="center")  # Desired height
    self.cur_height_tx = self.ax.text(cur_bar_center, HP[1] + HOF[1] + 0.01, 0, fontsize=FS, color=C["b"], ha="center", va="bottom", zorder=3)  # Current height
    self.des_height_tx = self.ax.text(des_bar_center, HP[1] + HOF[1] + 0.01, 0, fontsize=FS, color=C["r"], ha="center", va="bottom", zorder=3)  # Desired height
    # Value
    self.des_height = 0  # Desired height
    self.cur_height = 0  # Current height


# Update the height bars
def update_height(self, cur_height: float = 0, des_height: float = 0, slider: bool = True) -> None:
    self.cur_height_bar[0].set_height((cur_height) * HR if (cur_height) > 0 else 0)
    self.des_height_bar[0].set_height((des_height) * HR if (des_height) > 0 else 0)
    self.cur_height_tx.set_text(f"{cur_height:.2f}")  # Current height
    self.cur_height_tx.set_position((HP[0] + HOF[0] + HW * 0.5, HP[1] + HOF[1] + (cur_height) * HR + 0.01))  # Current height
    self.des_height_tx.set_text(f"{des_height:.2f}")  # Desired height
    self.des_height_tx.set_position((HP[0] + HOF[0] + HW * 1.5, HP[1] + HOF[1] + (des_height) * HR + 0.01))  # Desired height
    self.cur_height = cur_height  # Current height
    self.des_height = des_height  # Desired height
    # Update the slider value
    if slider:
        self.sliders[1].set_val(self.des_height)


# Add ticks to the height bar
def add_ticks_bar(self, left_edge: float) -> None:
    num_ticks = 30  # Total number of ticks
    tick_positions = np.linspace(HP[1] + HOF[1], HP[1] + HOF[1] + HH, num_ticks + 1)
    for i, pos in enumerate(tick_positions):
        # Calculate the tick's start and end points
        if i == 0:
            end_x = left_edge + HW
            linewidth = 1.5  # Thicker line for the first tick
        elif i % 10 == 0:  # Long tick every 10 units
            end_x = left_edge + HW / 3
            linewidth = 1.5  # Thicker line for long ticks
        elif i % 5 == 0:  # Middle tick every 5 units
            end_x = left_edge + HW * 2 / 7
            linewidth = 1.25  # Slightly thicker line for middle ticks
        else:  # Regular tick for other units
            end_x = left_edge + HW / 7
            linewidth = 1  # Standard line width for regular ticks
        self.ax.plot([left_edge, end_x], [pos, pos], color=C["w"], linewidth=LW, zorder=2)
    self.ax.plot([left_edge, left_edge], [HP[1] + HOF[1], HP[1] + HOF[1] + HH], color=C["w"], linewidth=1.5, zorder=2)


# Initialize the variables sliders
def init_variables(self) -> None:
    # Plot the debug rectangle of the variables sliders
    # self.ax.add_patch(patches.Rectangle(VP, VS[0], VS[1], linewidth=0.5, edgecolor=C["w"], fill=False, zorder=1))
    # Sliders
    self.variables = [0] * NCV  # List to store the created slider widgets
    self.sliders = []  # List to store the created slider widgets
    for key, value in V.items():
        # Extract the slider parameters from the value list
        label, min_val, max_val, init_val, val_step, slider_position = value

        # Create an axes instance for the slider
        axes = plt.axes(slider_position)

        # Create the slider
        slider = widgets.Slider(ax=axes, label=label, valmin=min_val, valmax=max_val, valinit=init_val, orientation="horizontal", initcolor=C["r"], track_color=C["a"], valstep=val_step, zorder=2)

        # Set additional slider properties
        slider.label.set_color(C["r"] if key[0] == "D" else C["g"])
        slider.label.set_fontsize(FS)
        slider.valtext.set_color(C["r"] if key[0] == "D" else C["g"])
        slider.poly.set_color(C["r"] if key[0] == "D" else C["g"])

        # Add the slider to the list
        self.sliders.append(slider)

        def slider_update(val, slider_ref):
            # slider_ref is a reference to the slider that was changed.
            label = slider_ref.label.get_text()
            if label == "Yaw ":
                self.des_yaw = val
                update_yaw(self, np.radians(self.cur_yaw), np.radians(self.des_yaw), slider=False)
            elif label == "Height ":
                self.des_height = val
                update_height(self, self.cur_height, self.des_height, slider=False)
            elif label == "force x ":
                self.variables[0] = val
            elif label == "z level ":
                self.variables[1] = val
            elif label == "t rotate ":
                self.variables[2] = val
            elif label == "angle ":
                self.variables[3] = val
            elif label == "zigzag ":
                self.variables[4] = val

        # Attach the callback with label identification
        for slider in self.sliders:
            slider.on_changed(lambda val, s=slider: slider_update(val, s))


# Initialize the battery indicator
def init_battery(self) -> None:
    # Plot the debug rectangle of the battery indicator
    # self.ax.add_patch(patches.Rectangle(BP, BS[0], BS[1], linewidth=0.5, edgecolor=C["w"], fill=False, zorder=1))
    # Plot the battery background
    self.ax.add_patch(patches.Rectangle((BP[0] + BOF[0], BP[1] + BOF[1]), BS[0] - 2 * BOF[0], BS[1] - 2 * BOF[1], facecolor=C["a"], fill=True, zorder=1))
    # Plot the battery level indicator
    self.battery_indicator = self.ax.barh(BP[1] + BS[1] / 2, 0, BS[1] - 2 * BOF[1], color=C["g"], left=BP[0] + BOF[0], zorder=2)
    # Plot the battery rectangle
    self.ax.add_patch(patches.Rectangle((BP[0] + BOF[0], BP[1] + BOF[1]), BR * MAXB, BS[1] - 2 * BOF[1], edgecolor=C["w"], fill=False, zorder=3))
    # Text
    self.ax.text(BP[0] + BS[0] / 2, BP[1] + BS[1], "Battery", fontsize=FS, color=C["w"], ha="center", va="bottom", zorder=1)  # Battery
    self.battery_tx = self.ax.text(BP[0] + BS[0] / 2, BP[1] + BS[1] / 2, "?V", fontsize=FS, color=C["w"], ha="center", va="center", zorder=3)  # Battery level
    # Value
    self.battry_level = 0  # Battery level


# Update the battery indicator
def update_battery(self, battry_level: float = 0) -> None:
    if battry_level > MAXB:
        battry_level = MAXB
    self.battry_level = battry_level
    self.battery_indicator[0].set_width(self.battry_level * BR)
    bar_color = C["g"]
    if self.battry_level <= BTH[1]:
        bar_color = C["r"]
    elif self.battry_level <= BTH[0]:
        bar_color = C["o"]
    self.battery_indicator[0].set_color(bar_color)
    self.battery_tx.set_text(f"{self.battry_level:.2f}V")  # Battery level
    self.battery_tx.set_color(C["k"])


# Initialize the distance indicator
def init_distance(self) -> None:
    # Plot the debug rectangle of the battery indicator
    # self.ax.add_patch(patches.Rectangle(BP, BS[0], BS[1], linewidth=0.5, edgecolor=C["w"], fill=False, zorder=1))
    # Plot the battery background
    self.ax.add_patch(patches.Rectangle((DP[0] + DOF[0], DP[1] + DOF[1]), DS[0] - 2 * DOF[0], DS[1] - 2 * DOF[1], facecolor=C["a"], fill=True, zorder=1))
    # Plot the battery level indicator
    self.distance_indicator = self.ax.barh(DP[1] + DS[1] / 2, 0, DS[1] - 2 * DOF[1], color=C["p"], left=DP[0] + DOF[0], zorder=2)
    # Plot the battery rectangle
    self.ax.add_patch(patches.Rectangle((DP[0] + DOF[0], DP[1] + DOF[1]), DR * MAXD, DS[1] - 2 * DOF[1], edgecolor=C["w"], fill=False, zorder=3))
    # Text
    self.ax.text(DP[0] + DS[0] / 2, DP[1] + DS[1], "Distance", fontsize=FS, color=C["w"], ha="center", va="bottom", zorder=1)  # Battery
    self.distance_tx = self.ax.text(DP[0] + DOF[0] * 1.5, DP[1] + DS[1] / 2, "0", fontsize=FS, color=C["w"], ha="left", va="center", zorder=3)  # Battery level
    # Value
    self.distance = 0  # Battery level


# Update the distance indicator
def update_distance(self, distance: float = 0) -> None:
    if distance > MAXD:
        distance = MAXD
    self.distance = distance
    self.distance_indicator[0].set_width(self.distance * DR)
    self.distance_tx.set_text(f"{self.distance:.1f}")  # Distance
    self.distance_tx.set_position((DP[0] + DOF[0] * 1.5 + self.distance * DR, DP[1] + DS[1] / 2))  # Distance


# Initialize the connection status indicator
def init_connection_status(self) -> None:
    self.connection_dot = self.ax.scatter(CP[0], CP[1], s=40, color=C["r"], zorder=1)
    self.connection_text = self.ax.text(CP[0] + COF, CP[1], "Send Failed", fontsize=FS, color=C["r"], ha="left", va="center", zorder=1)


# Update the connection status indicator
def update_connection_status(self, status: bool = False) -> None:
    self.connection_dot.set_color(C["g"] if status else C["r"])
    self.connection_text.set_text("Send Success" if status else "Send Failed")
    self.connection_text.set_color(C["g"] if status else C["r"])


# Initialize the buttons
def init_buttons(self):
    self.buttons = []
    for key, value in U.items():
        name, color, position = value
        hovercolor = C["g"]
        axes = plt.axes(position)
        self.buttons.append(widgets.Button(ax=axes, label=name, color=color, hovercolor=hovercolor))
    
    def button_update(event, button_ref):
        label = button_ref.label.get_text()
        return
        if label == "Send":
            print("Send")
        elif label == "Reset":
            print("Reset")
        elif label == "Close":
            print("Close")

    # Register the callback functions
    for button in self.buttons:
        button.on_clicked(lambda event, b=button: button_update(event, b))