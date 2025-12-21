from comm.Serial import SerialController, DataType_Int, DataType_Float, DataType_Boolean


from user_parameters import ROBOT_MACS, SERIAL_PORT, PRINT_JOYSTICK

# Function to send preferences to a specific robot
def send_preferences(serial, robot_mac, preferences):
    for pref in preferences:
        serial.send_preference(robot_mac, pref["data_type"], pref["key"], pref["value"])

# Main execution block
if __name__ == "__main__":
    # Communication setup
    serial = SerialController(SERIAL_PORT, timeout=0.5)

    # List of robots and their preferences
    robots = [
        # blue robot with skates and no net
        {"mac": "30:30:F9:34:66:FC", "preferences": [
            {"data_type": DataType_Boolean, "key": "zEn", "value": True},
            {"data_type": DataType_Float, "key": "kpyaw", "value": 2},
            # Add more preferences here
        ]},
        {"mac": "MAC2", "preferences": [
            {"data_type": DataType_Boolean, "key": "zEn", "value": True},
            {"data_type": DataType_Boolean, "key": "yawEn", "value": False},
            # Custom preferences for MAC2
        ]}
    ]



    # Sending common preferences to all robots
    for robot in ROBOT_MACS:
        serial.manage_peer("A", robot)
        serial.manage_peer("G", robot)
        
        # Send specific preferences
        for prefs in robots:
            if robot == prefs["mac"]:
                send_preferences(serial, robot, prefs["preferences"])
                break
        serial.send_control_params(robot, (0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 1, 0))


