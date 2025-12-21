"""
Author       : Hanqing Qi
Date         : 2023-11-11 14:54:50
LastEditors  : Hanqing Qi
LastEditTime : 2023-11-12 15:59:11
FilePath     : /GUI/SimpleGUI_V3/simpleGUIparams.py
Description  : Parameters for SimpleGUI V3
"""

# Colors
C = {
    "r": "#fa7970",  # Red
    "g": "#7ce38b",  # Green
    "o": "#faa356",  # Orange
    "p": "#cea5fb",  # Purple
    "k": "#161b22",  # Black
    "a": "#21262d",  # Gray
    "w": "#ecf2f8",  # White
    "c": "#a2d2fb",  # Cyan
    "b": "#77bdfb",  # Blue
    "y": "#c6cdd5",  # Yellow
    # "i": "#FF79C6",
}

# GUI parameters
GS = [6, 3.5]  # GUI size
FS = 10  # Font size
LW = 1.5  # Line width

# Yaw parameters
YP = [0 * GS[0], 0 * GS[1]]  # Position (left bottom corner) of yaw indicator
YS = [0.4 * GS[0], 0.4 * GS[0]]  # Size of yaw indicator
YOF = [0.05 * YS[0], 0.05 * YS[1]]  # Offset of yaw indicator (horizontal, vertical)
YC = [YP[0] + YS[0] / 2, YP[1] + YS[1] / 2]  # Center of yaw indicator
YR = 0.4 * YS[0]  # Radius of yaw indicator

# Height parameters
HP = [0.4 * GS[0], 0]  # Position (left bottom corner) of height indicator
HS = [0.2 * GS[0], 0.4 * GS[0]]  # Size of height indicator
HOF = [0.05 * HS[0], 0.05 * HS[1]]  # Offset of height indicator (horizontal, vertical)
HW = (HS[0] - 2 * HOF[0]) / 2  # Width of height indicator
HH = HS[1] - 2 * HOF[1]
MAXH = 15  # Maximum height
HR = (HS[1] - 2 * HOF[1]) / MAXH  # Height ratio

# Battery parameters
BP = [0, 0.8 * GS[1]]  # Position (left bottom corner) of battery indicator
BS = [0.2 * GS[0], 0.15 * GS[1]]  # Size of battery indicator
MAXB = 4.5  # Maximum battery
BOF = [0.05 * BS[0], 0.1 * BS[1]]  # Offset of battery indicator (horizontal, vertical)
BTH = [4, 3.5]  # Battery threshold
BR = (BS[0] - 2 * BOF[0]) / MAXB  # Width of battery indicator

# Distance parameters
DP = [0.2 * GS[0], 0.8 * GS[1]]  # Position (left bottom corner) of distance indicator
DS = [0.4 * GS[0], 0.15 * GS[1]]  # Size of distance indicator
MAXD = 500  # Maximum distance
DOF = [0.05 * DS[0], 0.1 * DS[1]]  # Offset of battery indicator (horizontal, vertical)
DR = (DS[0] - 2 * DOF[0]) / MAXD  # Width of battery indicator

# Connection parameters
CP = [0.1 * GS[0], 0.28 * GS[1]]  # Position (left bottom corner) of connection indicator
COF = 0.02 * GS[0]  # Offset of connection indicator


# Variables parameters
NCV = 5  # Number of custom variables
VA = 0.08  # Vertical spacing between sliders
VH = 0.1  # Adjust as per your layout needs
# name, min, max, init, step, axes
V = {
    "D1": ["Yaw ", -180, 180, 0, 1],
    "D2": ["Height ", 0, 15, 0, 0.1],
    # "P1": ["N/A ", -10, 10, 0, 1],
    # "P2": ["N/A ", -10, 10, 0, 1],
    # "P3": ["N/A ", -10, 10, 0, 1],
    # "P4": ["N/A ", -10, 10, 0, 1],
    # "P5": ["N/A ", -10, 10, 0, 1],
}
# Update the Y-coordinate for each slider dynamically
for i, key in enumerate(V.keys()):
    V[key].append([0.69, VH + i * VA, 0.2, 0.06])

# Button parameters
UCV = 3  # Number of custom buttons
UA = 0.08 # Vertical spacing between buttons
U = {
    "B1": ["N/A", C["b"]],
    "B2": ["N/A", C["o"]],
    "B3": ["N/A", C["r"]],
}
# Update the Y-coordinate for each button dynamically
UH = VH + len(V) * VA  # Adjust the additional offset as needed
for i, key in enumerate(U.keys()):
    U[key].append([0.69, UH + i * UA, 0.25, 0.06])

# Now you can use the 'variables' and 'B' dictionaries to create sliders and buttons
