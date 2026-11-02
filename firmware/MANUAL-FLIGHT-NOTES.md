# SwarmBase manual-control compensated firmware: notes

> **Historical record dated 2026-10-28**, translated from the author's notes. Several statements are out of date: for example the large-flip guard (section 3.2) is now disabled (`SERVO_FLIP_GUARD = false` in `src/robot/RawBicopter.cpp`), and later changes (paired thrust mixing, yaw-rate axis, pitch auto-zero, downward thrust hysteresis, IMU watchdog) are not described here. For setup and flashing see `FLASHING.md`; for the current behavior see the source comments. Links and paths point to the author's computer.

Updated: 2026-10-28. This document records the changes made on this machine, how to use them, and what was verified, based on the source and the flashing/test records up to 2026-10-28.

## 1. Versions and directories

| Part | Location on this machine | Purpose |
|---|---|---|
| Manual-control compensated firmware | [BlimpSwarm](/home/zhengqi-sun/Desktop/BlimpSwarm) | The modified version this document describes |
| PC ground station | [SwarmBase-main-main](/home/zhengqi-sun/Desktop/SwarmBase-main-main) | Reads the Xbox controller and sends control requests through the base board |
| Print.h reference firmware | [BlimpSwarm-PrintOnly](/home/zhengqi-sun/Desktop/BlimpSwarm-PrintOnly) | Original source with only the missing Print.h path added; used for comparison |
| Standalone simulation | [SwarmBase-MuJoCo](/home/zhengqi-sun/Desktop/SwarmBase-MuJoCo) | Manual control, camera and ToF feedback, multi-balloon path tests |

**Last confirmed hardware state (2026-10-28): the robot board runs the manual-control compensated version (ManualPlus) with the PWM and flip-wait fixes; the temporary base board still runs the Print version (PrintFix).** The compensated source and a restorable application image are kept on this machine; starting the ground station does not switch the firmware on the board. The firmware status is in the [current firmware record](/home/zhengqi-sun/Documents/Codex/2026-10-15/codex/work/active-firmware.json). The hardware state here follows the latest flashing and check records.

The ground-station joystick mapping fix is shared by both firmware versions. The board parameters were kept when switching to the reference version last time, so that comparison mainly changes the firmware implementation.

**Current state: the PWM and flip-wait fix is flashed to the robot and the powered-off bench check after a cold start passed; the mechanical behavior under power has not been accepted yet.**

## 2. Control chain and hardware

Control chain: Xbox controller → PC-side mapping → USB base board → ESP-NOW radio → robot manual behavior → PID and mixer → output compensation → motors and servos.

The PC sends operator requests; the robot's ESP32 runs the flight control. The PID structure and parameter system follow the original project; the mixer gained numeric guards and the output layer gained compensation.

| Device | Last confirmed model / build configuration | MAC address | Last confirmed serial port |
|---|---|---|---|
| Robot control board | ESP32-S3, 8 MB flash; XIAO_ESP32S3 configuration | `48:27:E2:E6:E6:44` | `/dev/ttyACM0` |
| Temporary base board | Plain ESP32, 4 MB flash; ESP32 Dev Module configuration | `A4:F0:0F:76:DF:AC` | `/dev/ttyUSB0` |

Port numbers can change with the connection order. The ground station's port must be the **base board's** port; the robot USB is mainly for flashing and log checks.

Pin labels in the compensated robot code: servo 1 is `D0`, servo 2 is `D1`, motor 1 is `D9`, motor 2 is `D10` (the board's D-pin labels).

## 3. Changes made

| Change | Behavior | Main files |
|---|---|---|
| Print.h path added | The original file copied to `src/util/Print.h` so the examples' include path works | `src/util/Print.h` |
| Released-controller input fix | Triggers normalized from `-1..1` to `0..1` with a release deadzone before computing the forward/back request | Ground station `robot/RobotMaster.py` |
| Servo direction numeric guard | Direction from vector length and `atan2`; with too little thrust the last valid angle is kept, and a default angle is used when there is no history yet | `src/robot/FullBicopter.cpp`, `.h` |
| Motor frequency unified | Both motors at 55 Hz; servos stay at 50 Hz | `src/robot/RawBicopter.cpp` |
| Stable servo PWM quantization | Servos use fixed 14-bit pulse quantization; no alternating between adjacent duty values | `src/act/AServo.cpp`, `.h` |
| Large-flip guard | Both motors drop to minimum output first, then the servo angle is locked and the guard waits before thrust may resume | `src/act/ServoFlipGuard.h`, `src/robot/RawBicopter.cpp` |
| Manual hold-target initialization | On first use and on stop, the held height and heading are initialized from the sensors | `src/state/nicla/ManualState.cpp`, `.h` |
| Command and output logs | Links each received command, behavior output, actuator request, PWM library setting and LEDC register reading | `examples/MultiRobotBicopter/MultiRobotBicopter.ino` and actuator files |

### 3.1 Servo PWM compensation

The original integer-degree to integer-microsecond mapping is kept. Servos now run at 50 Hz with 14-bit PWM, and the target pulse is rounded to the nearest available step; the same angle always gives the same step, instead of alternating adjacent duty values to average out the error. One step is about 1.22 µs. The motors still use 55 Hz, 10-bit PWM; the ESP32Servo library is unchanged.

End points still follow the library's limits; when the control loop is late it does not send a burst of catch-up writes, and the late frames are counted. This compensates software quantization error, not the servo's mechanical zero or the motor thrust calibration.

### 3.2 Flip guard

| Parameter | Value | Meaning |
|---|---:|---|
| `TRIGGER_DEG` | 100° | Largest angle-command change (scaled by `servoRange`) before the guard triggers |
| `COAST_US` | 650000 µs | Time both motors stay at minimum output while the servo command is held |
| `SETTLE_US` | 350000 µs | Time the new servo command is locked |

Sequence: normal output → a large flip is detected → both motors at minimum with the old servo angle held for 650 ms → the new servo angle is sent and locked for 350 ms → motor output may resume. Small target changes during the wait do not move the locked angle or restart the timer; if, at the end of the wait, the latest target again exceeds the 100° threshold, both motors stay at minimum, the new target is locked and the 350 ms wait restarts. The first entry into the output layer also goes through the lock wait; a stop request always keeps motor output at zero.

**The hardware has no motor speed / thrust feedback and no servo shaft angle feedback.** These conditions use angle-command differences and timed waits; they do not mean the motors were measured to have stopped or the servos to have arrived. 650 / 350 ms have not been calibrated under load on this machine.

## 4. Starting the ground station and the controller

First check that the base board and the Xbox controller are connected and that no other program holds the base serial port. The connection settings are in [user_parameters.py](/home/zhengqi-sun/Desktop/SwarmBase-main-main/user_parameters.py):

```python
robot_macs = ["48:27:E2:E6:E6:44"]
SERIAL_PORT = "/dev/ttyUSB0"
```

Main controller entry point:

```bash
cd /home/zhengqi-sun/Desktop/SwarmBase-main-main
.venv/bin/python RobotControl.py
```

No `--joystick` suffix is needed. To only watch the base and cached telemetry, without a controller:

```bash
.venv/bin/python RobotControl.py --monitor
```

### 4.1 Controller mapping

| Input | Current use |
|---|---|
| Left stick up/down | Request up / down |
| Right stick left/right | Request yaw turn |
| RT right trigger | Request forward |
| LT left trigger | Request backward; with RT pressed too, the two are subtracted |
| B | Toggle between stopped and manual run |
| A | Original autonomous state machine |
| X | Original balloon mode |
| Y | Original goal mode |
| LB / RB | Auxiliary channel; unused on this two-motor robot |
| Left stick left/right, right stick up/down | Not used for control |
| D-pad, Menu, View, stick clicks, etc. | Not bound |

Stick deadzone is 15%, trigger release deadzone 5%. Releasing the controls sets the motion request to zero but does not turn the run state off; height or attitude hold output may still be present. A / X / Y are the original project's autonomous functions, not the simulated multi-balloon path below, and are outside the scope of this manual-compensation acceptance.

### 4.2 Common keyboard keys

Keyboard input goes to the ground-station plot window; click the window first.

| Input | Use |
|---|---|
| `1` then Enter | Select robot 1 |
| `s` | Send stop; without a number it applies to all robots |
| `1` then `s` | Send stop to robot 1 |
| `p` | Upload the local parameter set |
| lowercase `b` / `g` | Original autonomous balloon / goal entry |
| `c` | Set the ESC calibration flag; no calibration was done in this work |

Controller B and keyboard lowercase `b` are different. Selecting a number and start/stop both send commands to the board; use `--monitor` to only watch the connection. When comparing firmware, keep the parameters and controller mapping the same; `p` uploads parameters and is not a start switch.

## 5. Parameters and logs

Parameters are stored in the robot's non-volatile storage (NVS); flashing the application area kept them. The PC-side [Preferences.py](/home/zhengqi-sun/Desktop/SwarmBase-main-main/Preferences.py) holds the uploadable configuration; it does not overwrite all board parameters at every start. After editing it, upload explicitly for it to take effect.

Common parameters: `zEn` / `yawEn` turn height / heading feedback on or off; `kpz` / `kdz` / `kiz` are the height PID gains; `lx` is the half distance between the motors; `servoRange` / `servoBeta` are the servo mapping parameters.

The compensated version's serial log runs at 115200 baud:

| Field | Meaning |
|---|---|
| `[CMD]`, `seq` | Received command and its sequence number |
| `[CFG]` | Snapshot of the flight-control parameters |
| `[EXEC]`, `beh` | Execution snapshot and the behavior vector from the state machine |
| `requested` / `out` | Actuator vector before / after compensation |
| `flip_phase` | 0 normal, 1 thrust-off wait, 2 servo-swing wait |
| `pwm_updates` / `pwm_late` | Servo PWM updates / late frames |
| `servo_ticks_set` | Latest integer servo PWM step written |
| `servo_tick_sum` / `servo_us_sum` | Accumulated steps written / accumulated intended pulse width, to check the average software error |
| `ledc1` to `ledc4` | Pin, channel, resolution, frequency, current-period duty reading |

These logs are software settings and register read-backs, not measurements of real thrust, speed, shaft angle or external waveforms. The Print.h reference version does not have these extra output logs.

## 6. Build configuration

The local toolchain is Arduino ESP32 core 2.0.17 and ESP32Servo 1.2.1, under `.toolchain` in the compensated version's directory.

Build the compensated robot firmware:

```bash
cd /home/zhengqi-sun/Desktop/BlimpSwarm
./firmware.sh build robot
```

`firmware.sh` uses the XIAO_ESP32S3 configuration by default, and `build base` also produces an ESP32-S3 base build. The temporary base board is a plain ESP32 and must be built with its own configuration:

```bash
cd /home/zhengqi-sun/Desktop/BlimpSwarm
.toolchain/bin/arduino-cli --config-file .toolchain/arduino-cli.yaml compile \
  --fqbn 'esp32:esp32:esp32:FlashSize=4M,PartitionScheme=default,FlashMode=dio,FlashFreq=40,UploadSpeed=115200,PSRAM=disabled' \
  --library "$PWD" --jobs 4 --build-path "$PWD/build/base-esp32-test" \
  "$PWD/examples/BaseTranseiver"
```

These commands only build. Base images for the two chips must not be mixed; the ESP32-S3 base source and builds are still kept in the project.

## 7. Verification done

The table below is the history before this output fix; the current candidate's verification is in section 12.

| Level | Verified | Evidence |
|---|---|---|
| Offline C++ | The actual modified source and the ESP32Servo library, tested against simulated GPIO / LEDC and clock; 100,000 guard-state inputs, start/stop, target changes mid-wait, invalid values and 32-bit timer wrap | [Offline test record](/home/zhengqi-sun/Documents/Codex/2026-10-15/codex/outputs/manual-compensation-offline-tests.json) |
| PWM software statistics | 1000 nominal 50 Hz updates, average pulse error under 0.02 µs on both sides; limits, late frames and 50 / 55 Hz settings passed | Same |
| Compensated version, hardware stopped check | 35 output snapshots; motors 55 Hz, servos 50 Hz, accumulated software PWM error and 12 stopped radio telemetry reads passed | [Hardware check record](/home/zhengqi-sun/Documents/Codex/2026-10-15/codex/outputs/manual-compensated-hardware.json) |
| Physics simulation of the ported guard | Hover, climb/descend and turn, 70 s each; no ground contact in the 90%-buoyancy model, largest horizontal drift under 0.5 mm, lowest height in climb/descend about 0.44 m | [Simulation record](/home/zhengqi-sun/Documents/Codex/2026-10-15/codex/outputs/manual-ported-guard-mujoco.json) |
| Print.h reference version | Robot and plain ESP32 base board both flashed and verified; attitude data after a cold start; 12 stopped telemetry reads passed | [Reference check record](/home/zhengqi-sun/Documents/Codex/2026-10-15/codex/outputs/print-only-stopped-hardware.json) |

After a warm reset of the compensated version the attitude fields were all zero; after switching to the Print.h reference version and a cold start, attitude data came back. The two results are recorded separately; the reference version's cold-start check is not a cold-start acceptance of the compensated version.

The simulation uses 120 g mass, 90% buoyancy and dynamics parameters that were not identified from measurements. Waveforms under load, motor speed, servo mechanical motion and free flight are not accepted yet. An earlier fixed 1 s + 1 s wait failed the climb/descend simulation; the version kept is 650 + 350 ms.

## 8. Backing up and restoring the compensated version

The [archive directory](/home/zhengqi-sun/Desktop/BlimpSwarm-backups/before-print-only-both-boards-20261027-183121) made before the last switch to the reference version contains:

| File | Content |
|---|---|
| `compensated-source.tar.gz` | Compensated version source |
| `robot-current-application-at-0x10000.bin` | Application read back live from the robot board, identical to the verified compensated image |
| `robot-current-prefix-and-application.bin` | Robot 0x0 to 0xD0000: bootloader, partitions, parameters, OTA data and the application at that time; not a full 8 MB image |
| `base-current-full-flash.bin` | Full 4 MB flash of the temporary base board |
| `base-current-application-at-0x10000.bin` | Copy of the base board application |
| `manifest.json`, restore and run notes (`.txt`) | Checksums, flashing record and restore notes |

To go back to the verified compensated image: first disconnect ESC power and servo power, close programs holding the serial port, check the robot identity and partition layout, then restore only the robot application:

```bash
cd /home/zhengqi-sun/Desktop/BlimpSwarm
python3 .toolchain/data/packages/esp32/tools/esptool_py/4.5.1/esptool.py \
  --chip esp32s3 \
  --port '/dev/serial/by-id/usb-Espressif_USB_JTAG_serial_debug_unit_48:27:E2:E6:E6:44-if00' \
  --baud 460800 write_flash \
  --flash_mode keep --flash_freq keep --flash_size keep --verify --no-progress \
  0x10000 '/home/zhengqi-sun/Desktop/BlimpSwarm-backups/before-print-only-both-boards-20261027-183121/robot-current-application-at-0x10000.bin'
```

This command writes to hardware; run it only after deciding to switch back to the compensated version. The base board has no robot output compensation logic, so the matching base program can usually stay when switching the robot back. After restoring, check the boot log and stopped telemetry before any test under load; the restore command was not run while writing this document.

The earlier [compensated development archive](/home/zhengqi-sun/Desktop/BlimpSwarm-backups/manual-flight-20261027-162608) also keeps the source before the changes, the old 8 MB flash from that time, and the compensated application and test archive.

## 9. Standalone simulation entry

Multi-balloon autonomous tracking lives in a separate MuJoCo project and was not flashed to the real robot with the manual firmware:

```bash
cd /home/zhengqi-sun/Desktop/SwarmBase-MuJoCo
python3 sim.py --viewer --balloon-path
```

After clicking the window: keypad `.` resets, Enter starts, `0` stops. Four balloons stay still and turn green one by one; the robot decides it lost the target only from the target missing in the image, searches after 0.3 s, then approaches with camera and ToF feedback and holds about 80% of the frame. After 3 s stable the scene activates the next balloon without telling the controller about the target change.

The [window test record](/home/zhengqi-sun/Desktop/SwarmBase-MuJoCo/outputs/balloon-path-native-window-test.json) finished the four points in about 112.8 s, with the final stable frame share about 77.6% to 82.4%. These results are simulation only and do not mean the real robot has this autonomous behavior.

## 10. Latest restore record (2026-10-28)

The robot was restored from the Print version to the previously verified ManualPlus application; the base board was not written. The robot's previous application and parameter / boot area were [archived live](/home/zhengqi-sun/Desktop/BlimpSwarm-backups/before-ManualPlus-restore-20261028-135417); the application flash verified, and the first 64 KB were byte-identical to before the restore. The stopped [re-check](/home/zhengqi-sun/Documents/Codex/2026-10-15/codex/outputs/ManualPlus-restored-20261028.json) after a USB cold start passed: 34 output snapshots, motors 55 Hz / servos 50 Hz, PWM accumulators and 12 radio telemetry reads normal, non-zero attitude data read. No motion requests were sent and no parameters were written; flight under load and the real speed / servo shaft angle were not verified.

## 11. Manual-control diagnostic display (2026-10-28)

The start command is unchanged. The display keeps the original heading dial, height bars, battery, distance, vision box and sliders, with the original control sizes and interaction; it only adds three status lines at the bottom, showing the PC mode and the action being sent, the telemetry age, the board's motor / servo outputs and the log status. The earlier multi-column diagnostic panel and thrust curves were removed from the default display; detailed TX/RX data, PWM counters and flip-guard records are still saved in the log file.

The base board still uses the original radio protocol. Detailed robot output comes from the optional robot USB log port (115200 baud), set by `ROBOT_LOG_PORT` and `ROBOT_LOG_MAC` in `user_parameters.py`; it is only read passively, never written and never reset. Without the robot USB the controller still works through the base, and the display clearly marks missing data; board data older than 3 s is marked stale. Do not let another program hold the robot log port at the same time.

Every start automatically writes the inputs (with UTC time and session-relative time), the full 13 parameters, the sent control packets, base responses, telemetry and robot log to `logs/<timestamp>/session.jsonl` in the ground-station directory. A PC serial write does not prove radio delivery; base telemetry is a cache and does not prove the robot's sample time. A content match of repeated commands is not a per-packet confirmation. The board log shows the outputs the software tried to apply; there is no feedback of motor speed, real servo angle or real forward speed. Press `s` to stop first; closing the window does not stop the robot.

This change only touched the PC display and observation / logging; firmware and controller mapping were not changed. An offline comparison of 501 old/new parameter sets passed; byte-wise control packet comparison, fake serial port, disconnect / stale data, log-write failure and display rendering were verified; it was not tested together with the real robot.

## 12. PWM and flip-wait fix (2026-10-28, offline stage)

The source changes are only `src/act/AServo.cpp`, `AServo.h` and `ServoFlipGuard.h`; controller mapping, PID / parameters, mixer and ground-station display are unchanged. The 133 files before the change and the last verified old application image were [archived](/home/zhengqi-sun/Desktop/BlimpSwarm-backups/before-pwm-guard-fix-20261028-144925); the old application is a copy of the image read back and verified earlier, and the flash was not read again in this round.

The [offline tests](/home/zhengqi-sun/Documents/Codex/2026-10-15/codex/outputs/pwm-guard-fix-offline-tests-20261028.json) built the actual actuator source and the ESP32Servo library with the hardware calls stubbed: a fixed angle for 1000 frames with no pulse alternation, all 181 integer angles stable for 25 frames each, largest quantization error about 0.607 µs; servo 14-bit / 50 Hz and motor 10-bit / 55 Hz isolation passed. Lock wait, recovery under noise, another large reversal, stop, invalid input, 32-bit timer wrap and 100,000 random tests passed, with address and undefined-behavior sanitizers enabled.

In a sparse replay of the bench 2 Hz request samples, forward and backward both recovered non-zero output. The same samples were also linearly interpolated to 250 Hz and the new and old guards compared from a common lock-wait state; that interpolated replay is a constructed test and does not reproduce every control cycle of the bench or the real hardware behavior.

The ESP32-S3 candidate firmware [built successfully](/home/zhengqi-sun/Documents/Codex/2026-10-15/codex/outputs/pwm-guard-fix-robot-build-20261028.json); this offline stage did not flash, connect a serial port or send any command; the on-board results are in section 13. The fix only removes PWM alternation at a fixed angle and the endless wait caused by small target changes; servo angle changes from height feedback itself, real jitter and speed differences are not accepted on the real robot yet. 650 / 350 ms are still wait parameters not calibrated under load.

## 13. Fixed version flashed and powered-off bench check (2026-10-28)

Only the robot's `0x10000` application area was written and the image verified; the original first 64 KB (boot / partitions / parameters / OTA) were byte-identical before and after, and the base board was not written. The old application was [backed up live](/home/zhengqi-sun/Desktop/BlimpSwarm-backups/before-fixed-pwm-guard-flash-20261028-150203) before flashing; this is not a full 8 MB backup.

The user confirmed ESC power and servo power stayed disconnected with USB power only, and a robot USB cold start was done after the warm reset had shown all-zero attitude. [This round's check](/home/zhengqi-sun/Documents/Codex/2026-10-15/codex/outputs/fixed-pwm-guard-hardware-summary-20261028.json) passed: with fixed 135° / 45° commands the two PWM steps stayed at 1618 / 840, the library's microsecond readings were 1975 / 1025, the LEDC duty registers matched the settings, and servo 14-bit / 50 Hz and motor 55 Hz were as expected; the physical pin waveforms were not measured with an oscilloscope.

Eight request groups (stop, release, up, release up, down, forward, backward, final stop) matched the values received on the board bit for bit, with 8 linked output snapshots per group. Up/down and forward/backward all recovered non-zero final output; in the RUN phase the motor output matched the computed request, in COAST / SETTLE both were zero, and the final cleanup stop was confirmed received and executed. No parameters were written in this round, and real speed, real servo shaft angle and free flight were not tested.

Hold mode still changes the servo angle through height and other feedback, and some segments still triggered brief guard thrust cuts; so this round passing means the fixed-angle PWM no longer alternates and the four directions no longer get stuck, not that all mechanical twitching and speed differences are gone. Radio telemetry was not queried again in this round; TX/RX comparison used the radio CMD and the robot USB output log.
