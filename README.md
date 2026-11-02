# SwarmBase

Ground station (PC) and robot firmware for the bicopter blimp.

## Current state of the hardware (as handed over, 2026-11-02)

- **Robot** (XIAO ESP32S3, MAC `48:27:E2:E6:E6:44`): runs the **`robot-printonly`** firmware (original firmware + `Print.h`; image SHA-256 `957d9847…b5f`).
- **Base station** (plain ESP32, 4 MB): runs the original `BaseTranseiver`, identical in all branches; no reflash needed.
- **Parameters stored on the robot** are left over from earlier tests and may not match either branch. Press `p` with the branch's `Preferences.py` after flashing.

## Branches

- **`modified-blimpswarm` (this branch, recommended)**: newest version. Ground station and robot firmware with fixes for the known flight problems (motor thrust mixing, yaw sensing, pitch compensation, IMU start-up), controlled downward thrust, and Windows support.
- **`robot-printonly`**: what the robot runs now. Same ground station with the **original** robot firmware, with only `Print.h` added. RT flies backward, and heading hold is unreliable on this robot.
- **`main`**: the original ground station only (no firmware). Set up for Windows (`COM12`); on Linux the controller mapping is wrong.

Flash and use this branch. If something goes wrong, switch to `robot-printonly` (original firmware); its build commands are the same, but use that branch's `Preferences.py`.

## Quick start

Full details, the boot-log check, the Windows commands and known limitations are in [firmware/FLASHING.md](firmware/FLASHING.md). **Remove the propellers** until the bench checks pass.

1. **Install the build tools** (once; [arduino-cli](https://arduino.github.io/arduino-cli/latest/installation/) first):
   ```bash
   arduino-cli config init
   arduino-cli config add board_manager.additional_urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
   arduino-cli core update-index
   arduino-cli core install esp32:esp32@2.0.17
   arduino-cli lib install "ESP32Servo@1.2.1" "SparkFun BNO08x Cortex Based IMU@1.0.6" "Adafruit BMP3XX Library@2.1.6" "Adafruit BusIO@1.17.4" "Adafruit Unified Sensor@1.1.15" "IBusBM@1.1.4"
   ```
2. **Flash the robot** (USB to the robot; `arduino-cli board list` shows the port):
   ```bash
   arduino-cli compile --fqbn "esp32:esp32:XIAO_ESP32S3:USBMode=hwcdc,CDCOnBoot=default,FlashSize=8M,PartitionScheme=default_8MB,UploadSpeed=115200,PSRAM=disabled" --library firmware --build-path build/robot firmware/examples/MultiRobotBicopter
   arduino-cli upload --fqbn "esp32:esp32:XIAO_ESP32S3:USBMode=hwcdc,CDCOnBoot=default,FlashSize=8M,PartitionScheme=default_8MB,UploadSpeed=115200,PSRAM=disabled" --input-dir build/robot --port <robot-port> firmware/examples/MultiRobotBicopter
   ```
   Then unplug USB and battery for 10 s and power up again, so the IMU starts cleanly.
3. **Set up the ground station**:
   ```bash
   python3 -m venv .venv
   .venv/bin/pip install pyserial pygame matplotlib numpy
   ```
   In `user_parameters.py`, set `robot_macs` to the robot's MAC and `SERIAL_PORT` to the base station's port.
4. **Run it** with the Xbox controller connected: `.venv/bin/python RobotControl.py`. Click the dashboard window, press `1` then `Enter` to select the robot, then `p` to send the parameters.
5. **Bench checks** before flying (propellers off): see [FLASHING.md section 7](firmware/FLASHING.md#7-checks-before-the-first-flight-propellers-off).

## Controls

Xbox controller (applies to the selected robot):

| Input | Action |
|---|---|
| **B** | Off ↔ Manual. **Tap it**; holding it toggles repeatedly. |
| Left stick up / down | Height up / down. Pushing down past about half also turns the thrust downward (motors pause about 0.5 s). |
| Right stick left / right | Turn |
| RT | Forward |
| LT | Backward |
| A / X / Y | Autonomous Auto / Balloon / Goal (all track balloons with this firmware) |
| LB / RB | Not used |

Releasing the sticks holds height and heading; it does **not** stop the robot.

Keyboard (click the dashboard window first):

| Key | Action |
|---|---|
| `1`, then `Enter` | Select robot 1 |
| `s` | Stop all robots (fastest stop) |
| `p` | Send `Preferences.py` to the robot |
| `c` | ESC calibration on the next power-up: full throttle for 8 s. **Propellers off!** |
| `F1`–`F4` | Balloon color: purple / green / purple+green / red |
| `H` | Show the full quick reference |

All keys and the dashboard are described in [CONTROLS.md](CONTROLS.md).

## About this branch

Main changes from the original project:
- Each motor's thrust and direction are computed from the same vector (the original paired them crosswise, which reversed the yaw torque once the forward part outweighed the lift); yaw tilt limit, and the yaw command is scaled down at high thrust (`yawAuthRef`).
- Selectable yaw-rate axis (`yawRateAxis=7`: the IMU is mounted on its side, so gyro y is the heading rate).
- Pitch compensation: zero captured automatically while Off, limited to ±25°.
- Downward thrust: up/down switch with hysteresis on the height error (`zDownErr`, `zDownMs`); the motors are cut while the servos flip (`zCoastMs`, `zSwingMs`); no more full-turn servo swings at ±180° when flying backward.
- Both motors at 55 Hz PWM, fixed 14-bit servo quantization, manual hold targets initialized from the sensors.
- IMU: the watchdog counts only polling time and no longer forces a re-initialization; the `softReset()` start-up sequence is restored.
- Telemetry health pages (attitude, outputs, health) and a USB execution log.

Not yet verified on the real robot: downward thrust hysteresis, and whether the IMU data stream stays continuous (attitude is read on a still bench on 2026-11-02, not yet confirmed while moving).

`Preferences.py` is set for this firmware (`pitchEn=True`, `botZlim=-0.5`); flash this firmware before pressing `p`.

Not included: flight logs `logs/`, `.venv`, build outputs, the toolchain, local backups, and the upstream `docs/`. Historical notes: `firmware/MANUAL-FLIGHT-NOTES.md`.
