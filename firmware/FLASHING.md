# Building and flashing the firmware (modified-blimpswarm branch)

This guide flashes the firmware in `firmware/` to the robot and walks through the setup before the first power-up.
Run every command from the **repository root** (the directory with `RobotControl.py` and `firmware/`).

## 0. Hardware

| Board | Chip | Role | Program to flash |
|---|---|---|---|
| Robot control board | Seeed XIAO ESP32S3 (8 MB) | Flight control; drives motors and servos, reads IMU, barometer and camera | `firmware/examples/MultiRobotBicopter` |
| Base station (radio board) | Plain ESP32 (4 MB) or ESP32-S3 | Plugs into the PC over USB and talks to the robot over ESP-NOW | `firmware/examples/BaseTranseiver` |

**The base station usually does not need reflashing**: this branch's base program is identical to the original; if the base you received works, skip section 4.

> ⚠️ **Remove the propellers** for flashing, calibration and bench tests.

## 1. Install the build environment (once)

Use the versions below; the firmware was built and flown with them.

| Component | Version |
|---|---|
| arduino-cli | 1.x (tested with 1.5.1) |
| Arduino ESP32 core `esp32:esp32` | **2.0.17** (not 3.x) |
| ESP32Servo | 1.2.1 |
| SparkFun BNO08x Cortex Based IMU | 1.0.6 |
| Adafruit BMP3XX Library | 2.1.6 |
| Adafruit BusIO | 1.17.4 |
| Adafruit Unified Sensor | 1.1.15 |
| IBusBM | 1.1.4 |

Install arduino-cli: see <https://arduino.github.io/arduino-cli/latest/installation/> (on Windows, unzip the download and add the folder to PATH). Then:

```bash
arduino-cli config init
arduino-cli config add board_manager.additional_urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
arduino-cli core update-index
arduino-cli core install esp32:esp32@2.0.17
arduino-cli lib install "ESP32Servo@1.2.1" "SparkFun BNO08x Cortex Based IMU@1.0.6" "Adafruit BMP3XX Library@2.1.6" "Adafruit BusIO@1.17.4" "Adafruit Unified Sensor@1.1.15" "IBusBM@1.1.4"
```

On Linux, also add yourself to the serial group and log in again: `sudo usermod -aG dialout $USER`.

> The Arduino IDE works too: install esp32 2.0.17 in the Boards Manager and the libraries above in the Library Manager, copy the `firmware` folder into Arduino's `libraries/` as `BlimpSwarm`, select the "XIAO_ESP32S3" board and match the options in the FQBN below.

## 2. Find the serial ports

```bash
arduino-cli board list
```

- Robot: USB to the XIAO board; usually `/dev/ttyACM0` on Linux, `COMx` on Windows ("USB JTAG/serial debug unit").
- Base station: usually `/dev/ttyUSB0` on Linux, `COMx` on Windows (CH340/CP210x).

Below, replace `<robot-port>` and `<base-port>` with the actual names.

## 3. Build and flash the robot

```bash
arduino-cli compile --fqbn "esp32:esp32:XIAO_ESP32S3:USBMode=hwcdc,CDCOnBoot=default,FlashSize=8M,PartitionScheme=default_8MB,UploadSpeed=115200,PSRAM=disabled" --library firmware --build-path build/robot firmware/examples/MultiRobotBicopter
```

On success the last line reads `Sketch uses 776109 bytes (23%) ...` (the number may differ slightly).

```bash
arduino-cli upload --fqbn "esp32:esp32:XIAO_ESP32S3:USBMode=hwcdc,CDCOnBoot=default,FlashSize=8M,PartitionScheme=default_8MB,UploadSpeed=115200,PSRAM=disabled" --input-dir build/robot --port <robot-port> firmware/examples/MultiRobotBicopter
```

On success every section shows `Hash of data verified.`. Flashing **does not erase** the parameters stored on the board (NVS).

If the upload fails: hold the board's **B (BOOT) button**, plug in USB, release the button, and run upload again.

## 4. (If needed) Build and flash the base station

Plain ESP32 base:

```bash
arduino-cli compile --fqbn "esp32:esp32:esp32:FlashSize=4M,PartitionScheme=default,FlashMode=dio,FlashFreq=40,UploadSpeed=115200,PSRAM=disabled" --library firmware --build-path build/base-esp32 firmware/examples/BaseTranseiver
arduino-cli upload --fqbn "esp32:esp32:esp32:FlashSize=4M,PartitionScheme=default,FlashMode=dio,FlashFreq=40,UploadSpeed=115200,PSRAM=disabled" --input-dir build/base-esp32 --port <base-port> firmware/examples/BaseTranseiver
```

ESP32-S3 base: use the robot FQBN from section 3 in both commands and `build/base-s3` instead of `build/base-esp32`.
**Programs for the two chips cannot be swapped**; check which chip the base has first.

## 5. Check the robot boot log

```bash
arduino-cli monitor -p <robot-port> -c baudrate=115200
```

(Opening the port restarts the robot once; that is normal. `Ctrl+C` exits.) You should see:

```
Start!
ESP Board MAC Address:  48:27:E2:E6:E6:44      <- write this MAC down
BNO Initialization!
  BNO started: 1
Sensor was reset
Setting desired reports
Gryo Integrated Rotation vector enabled
...
```

- `Ooops, no BNO085 detected`, or no `Sensor was reset` at all: **unplug USB and battery, wait 10 s, power up again** (a stuck IMU only recovers from a full power-off), then check again. If it still fails, check the IMU's I2C wiring.
- `Main Base Not Set.`: a new robot has not paired with the base yet; starting the ground station in section 6 pairs it automatically. If telemetry still does not arrive, power-cycle the robot once.

## 6. Set up the ground station and send the parameters

The ground station runs on Linux, macOS and Windows. On Windows the robot USB log is not read (`ROBOT_LOG_PORT` is ignored and the dashboard shows "Robot USB log not supported on this OS"); wireless control and the ground-station log in `logs/` are unaffected.

1. Install the Python dependencies (in the repository root; tested with Python 3.12, pyserial 3.5, pygame 2.6.1, matplotlib 3.6.3, numpy 1.26.4):
   ```bash
   sudo apt install python3-tk        # Ubuntu/Debian: needed for the dashboard window
   python3 -m venv .venv
   .venv/bin/pip install pyserial pygame matplotlib numpy
   ```
   Windows (tcl/tk is included by the Python installer by default):
   ```bat
   python -m venv .venv
   .venv\Scripts\python -m pip install pyserial pygame matplotlib numpy
   ```
2. Edit `user_parameters.py`:
   - `robot_macs = ["<MAC from section 5>"]`
   - `SERIAL_PORT = "<base-port>"` (on Windows, like `"COM5"`)
   - `ROBOT_LOG_PORT`: the robot's USB log port (optional, logging only); leave it as is if unused, a missing port is skipped.
3. Connect the Xbox controller and start:
   ```bash
   .venv/bin/python RobotControl.py
   ```
   Windows: `.venv\Scripts\python RobotControl.py`
4. Click the dashboard window once, press `1` then `Enter` to select the robot, then press **`p` to send the parameters**.
   `Preferences.py` is set for this firmware (`pitchEn=True`, `botZlim=-0.5`, ...). **Flash this firmware before pressing `p`**; older firmware misbehaves with these parameters.

Controls are described in `CONTROLS.md` in the repository root.

## 7. Checks before the first flight (propellers off)

1. **ESC throttle-range calibration** (required for new or replaced ESCs): with the robot selected, press `1` then `c`, then unplug USB and battery for a full power-off and power up again. After power-up the motors **do not spin**; each ESC beeps a tone group at the high point and at the low point, about 20 s in total. Then power-cycle once more and confirm it does not calibrate again.
2. Controller **B** enters manual mode: both servos point up.
3. Slowly push the left stick up: both motors should start together; at high throttle both should sound the same (if not, check the ESCs first).
4. Press **RT**: both servos tilt forward the same way (forward); push the right stick left/right: the two servos tilt in opposite directions.
5. Hold the robot and slowly turn it left and right: the dashboard heading dial should follow (IMU working).
6. Keyboard `s` or controller **B** stops.

Only when all of this is correct, fit the propellers and test-fly low, one action at a time. Flight logs are saved in `logs/`.

## 8. Going back to the original firmware

The `firmware/` of this repository's `robot-printonly` branch is the original firmware (only `Print.h` added); build and flash commands are the same. Its `Preferences.py` differs (`pitchEn=False`, `botZlim=0`), so switch the ground station to that branch as well.

## Known limitations

- The robot USB log is not recorded on Windows (see section 6).
- The Xbox controller's raw axis numbers differ between Windows and Linux; `input/JoystickManager.py` picks them by OS (Linux tested; Windows follows the XInput order from the pygame documentation: right stick 2/3, LT 4, RT 5). macOS uses the Linux numbers and is untested.
- Windows support was verified by simulation on Linux and **has not run on a real Windows computer**. On first use on Windows, remove the propellers, enter manual mode and try each stick and trigger one at a time, checking the servo/motor responses in steps 3 and 4 of section 7; with every stick and trigger released there must be no movement.

## Not yet verified on the real robot

- Downward thrust hysteresis (`zDownErr` and related): passed in simulation, not flown.
- Whether the IMU data stream stays continuous: attitude is read on a still bench; not yet confirmed while the robot is moving (step 5 of section 7 is this check).
