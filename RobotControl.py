from comm.Serial import DataType_Boolean
from user_parameters import ROBOT_MACS, TENSILE_MASTER, TENSILE_FOLLOWERS, DEFENDER_MACS
from robot.RobotMaster import RobotMaster
import Preferences
import time
import importlib

PRINT_JOYSTICK = True
        
def startAutonomousBall(serial, robot, args):
    serial.send_control_params(robot, (3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    time.sleep(.2)
    serial.send_control_params(robot, (2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    time.sleep(.2)
    return 2

def startAutonomousGoal(serial, robot, args):
    serial.send_control_params(robot, (4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    time.sleep(.2)
    serial.send_control_params(robot, (2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    time.sleep(.2)
    return 2

def stopOne(serial, robot, args):
    serial.send_control_params(robot, (5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    time.sleep(.05)
    serial.send_control_params(robot, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    time.sleep(.05)
    return 0

def sendCalibrate(serial, robot, args):
    serial.send_control_params(robot, (5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    time.sleep(.05)
    serial.send_preference(robot, DataType_Boolean, "calibrate", True)
    time.sleep(.05)
    return -1

def controlTensileFollowers(serial, robot, args):
    serial.send_control_params(robot, (args[0], args[0], args[1], args[1], 0, 0, 0, 0, 0, 0, 0, 0, 0))
    time.sleep(.05)
    return 1


def sendPreferences(serial, robot, args):
    importlib.reload(Preferences)

    for pref in Preferences.PREFERENCES["ff:ff:ff:ff:ff:ff"]:
        serial.send_preference(robot, pref["data_type"], pref["key"], pref["value"])
    if robot not in Preferences.PREFERENCES:
        serial.send_control_params(robot, (0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 1, 0))
        return -1
    prefer = Preferences.PREFERENCES[robot]
    for pref in prefer:
        serial.send_preference(robot, pref["data_type"], pref["key"], pref["value"])
    serial.send_control_params(robot, (0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 1, 0))
    return -1

def sendOrangePreferences(serial, robot, args):
    importlib.reload(Preferences)

    for pref in Preferences.PREFERENCES["orange"]:
        serial.send_preference(robot, pref["data_type"], pref["key"], pref["value"])
    if robot not in Preferences.PREFERENCES:
        serial.send_control_params(robot, (0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 1, 0))
        return -1
    prefer = Preferences.PREFERENCES[robot]
    for pref in prefer:
        serial.send_preference(robot, pref["data_type"], pref["key"], pref["value"])
    serial.send_control_params(robot, (0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 1, 0))
    return -1

def sendYellowPreferences(serial, robot, args):
    importlib.reload(Preferences)

    for pref in Preferences.PREFERENCES["yellow"]:
        serial.send_preference(robot, pref["data_type"], pref["key"], pref["value"])
    if robot not in Preferences.PREFERENCES:
        serial.send_control_params(robot, (0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 1, 0))
        return -1
    prefer = Preferences.PREFERENCES[robot]
    for pref in prefer:
        serial.send_preference(robot, pref["data_type"], pref["key"], pref["value"])
    serial.send_control_params(robot, (0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 1, 0))
    return -1

def sendDefenderPreferences(serial, robot, args):
    importlib.reload(Preferences)

    for pref in Preferences.PREFERENCES["defender"]:
        serial.send_preference(robot, pref["data_type"], pref["key"], pref["value"])
    if robot not in Preferences.PREFERENCES:
        serial.send_control_params(robot, (0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 1, 0))
        return -1
    prefer = Preferences.PREFERENCES[robot]
    for pref in prefer:
        serial.send_preference(robot, pref["data_type"], pref["key"], pref["value"])
    serial.send_control_params(robot, (0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 1, 0))
    return -1

def sendAttackerPreferences(serial, robot, args):
    importlib.reload(Preferences)

    for pref in Preferences.PREFERENCES["attacker"]:
        serial.send_preference(robot, pref["data_type"], pref["key"], pref["value"])
    if robot not in Preferences.PREFERENCES:
        serial.send_control_params(robot, (0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 1, 0))
        return -1
    prefer = Preferences.PREFERENCES[robot]
    for pref in prefer:
        serial.send_preference(robot, pref["data_type"], pref["key"], pref["value"])
    serial.send_control_params(robot, (0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 1, 0))
    return -1

def monitor_base():
    """Check the base serial port with the original GUI; only sends I queries, no joystick needed."""
    import struct
    import serial as pyserial
    import matplotlib.pyplot as plt
    from comm.Serial import SerialController
    from gui.simpleGUI import SimpleGUI
    from user_parameters import SERIAL_PORT

    controller = SerialController(SERIAL_PORT, timeout=0.2)
    port = controller.serial
    gui = None
    try:
        port.exclusive = True
        gui = SimpleGUI("nicla")
        gui.fig.set_size_inches(10, 6, forward=True)
        gui.fig.canvas.manager.set_window_title(
            f"SwarmBase - Base monitor ({SERIAL_PORT})")
        gui.fig.suptitle(f"{SERIAL_PORT} | 115200 baud | Waiting for base",
                         color="white", fontsize=11)
        print(f"MONITOR_PORT={SERIAL_PORT} BAUD=115200", flush=True)
        # Matches this ESP32's auto-download circuit; reset, then record the real boot output.
        port.dtr = False
        port.rts = True
        time.sleep(0.15)
        port.rts = False
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and plt.fignum_exists(gui.fig.number):
            boot = port.read_all()
            if boot:
                print("BASE_BOOT", repr(boot), flush=True)
            plt.pause(0.05)
        window = gui.fig.canvas.manager.window
        print(f"GUI_WINDOW_ID=0x{window.winfo_id():x}", flush=True)
        previous = None
        samples = 0
        while plt.fignum_exists(gui.fig.number):
            sensors = None
            error = None
            try:
                port.reset_input_buffer()
                port.write(b"I")
                response = port.read(26)
                if len(response) == 26 and response.endswith(b"\r\n"):
                    sensors = struct.unpack("<6f", response[:24])
                connected = response == b"No Data.\r\n" or sensors is not None
            except (pyserial.SerialException, OSError) as exc:
                response, connected, error = b"", False, str(exc)
            state = (connected, sensors is not None, error)
            samples += 1
            if samples <= 5 or state != previous:
                print(f"BASE_QUERY {samples}: connected={connected} "
                      f"telemetry={sensors is not None} rx={response!r}"
                      + (f" error={error}" if error else ""), flush=True)
            previous = state
            values = sensors or (0.0,) * 6
            gui.update(cur_height=values[0], cur_yaw=values[1],
                       x=values[2], y=values[3], width=values[4], height=values[4],
                       battery=values[5], connection_status=connected)
            gui.connection_text.set_text("Base connected" if connected
                                         else "Base disconnected")
            telemetry = "Robot telemetry: base cache" if sensors is not None else "Robot telemetry: no data (gauges are placeholders)"
            gui.fig.suptitle(f"{SERIAL_PORT} | 115200 baud | {telemetry}",
                             color="white", fontsize=10)
            gui.fig.canvas.draw_idle()
            plt.pause(0.3)
    except KeyboardInterrupt:
        pass
    finally:
        controller.close()
        if gui is not None:
            plt.close(gui.fig)
        print("Base monitor closed; serial port released.", flush=True)


def main():
    robot_master = None
    from input.JoystickManager import JoystickManager
    try:
        robot_master = RobotMaster(0.3)
        joystick = JoystickManager()
        macs = ROBOT_MACS + DEFENDER_MACS + TENSILE_MASTER + TENSILE_FOLLOWERS
        robot_master.setup(macs, "nicla")
        followers = [i + 1 for i in list(range(len(macs) - len(TENSILE_FOLLOWERS), len(macs)))]

        robot_master.functionFactory('s', stopOne, "Stop")
        robot_master.functionFactory('b', startAutonomousBall, "Auto Ball")
        robot_master.functionFactory('g', startAutonomousGoal, "Auto Goal")
        robot_master.functionFactory('c', sendCalibrate, "Calibrate")
        robot_master.functionFactory('p', sendPreferences, "Send Preferences")
        robot_master.functionFactory('a', sendAttackerPreferences, "Send Attacker Preferences")
        robot_master.functionFactory('d', sendDefenderPreferences, "Send Defender Preferences")
        robot_master.functionFactory('f', controlTensileFollowers, "Controlling Follower")
        robot_master.functionFactory('y', sendYellowPreferences, "Send Yellow Preferences")
        robot_master.functionFactory('o', sendOrangePreferences, "Send Orange Preferences")

        index = "0"
        power = 1.
        angle = 90

        while True:
            time.sleep(0.2)
            keys = robot_master.get_last_n_keys(1)
            axis, buttons = joystick.getJoystickInputs()
            robot_master.processManual(axis, buttons, print_vals=True)
            if robot_master.mygui.closed:
                break

            power = min(1, max(0, power))
            angle = min(180, max(-180, angle))
            

            # Display joystick values if enabled
            if PRINT_JOYSTICK:
                print(" ".join(["{:.1f}".format(num) for num in axis]), buttons)

            if len(keys) == 0:
                continue
            
            key_pressed = keys[0]
            
            if key_pressed == 'enter':
                i = int(index)
                robot_master.switchRobot(i)
                index = "0"
            elif key_pressed in ('f1', 'f2', 'f3', 'f4'):
                # F1 purple, F2 green, F3 purple+green, F4 red
                robot_master.setColor(int(key_pressed[1]))
            elif len(key_pressed) == 1 and 32 <= ord(key_pressed) <= 127:
                if '0' <= key_pressed <= '9':
                    index += key_pressed
                elif key_pressed == '[':
                    for i in followers:
                        robot_master.runFunction('f', i, 0, 0)
                elif key_pressed == ']':
                    for i in followers:
                        robot_master.runFunction('f', i, power, angle)
                elif key_pressed == '=':
                    angle += 5
                    for i in followers:
                        robot_master.runFunction('f', i, power, angle)
                elif key_pressed == '-':
                    angle -= 5
                    for i in followers:
                        robot_master.runFunction('f', i, power, angle)
                elif key_pressed == ';':
                    power -= 0.05
                    for i in followers:
                        robot_master.runFunction('f', i, power, angle)
                elif key_pressed == '\'':
                    power += 0.05
                    for i in followers:
                        robot_master.runFunction('f', i, power, angle)
                elif key_pressed == 's':
                    power = 0
                    angle = 45
                    i = int(index)
                    robot_master.runFunction(key_pressed, i)
                    index = "0"
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
        if robot_master is not None:
            try:
                if robot_master.serial is not None:
                    robot_master.serial.close()
            finally:
                robot_master.diagnostics.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SwarmBase ground control")
    parser.add_argument("--monitor", action="store_true",
                        help="Only monitor the base connection and telemetry; no joystick needed")
    if parser.parse_args().monitor:
        monitor_base()
    else:
        main()