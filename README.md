# SwarmBase

Branch `robot-printonly`: the setup actually running on the robot on 2026-11-02.

- Repository root: PC ground station (local modified version: controller mapping fix, flight logs, dashboard); controls are described in `CONTROLS.md`.
- `firmware/`: robot firmware BlimpSwarm-PrintOnly, i.e. the original project source with only `src/util/Print.h` added.

Known behavior of this firmware:
- `fx` is negated in the firmware: on the controller **RT flies backward and LT flies forward**.
- The yaw loop uses gyro z; this robot's IMU is mounted on its side, so gyro z is actually the side-to-side swing rate.
- The two motors run at 55 Hz / 58 Hz PWM.
- `Preferences.py` is set for this firmware: `pitchEn=False` (the firmware adds the raw IMU angle, about +90° with the side mount) and `botZlim=0` (no up/down hysteresis).
- After flashing, an ESP-only reset cannot find the IMU; unplug USB and battery for a full power-off.
- The ground station here runs on Linux and macOS; Windows support is in the `modified-blimpswarm` branch.

Build and flash (needs Arduino ESP32 core 2.0.17 and ESP32Servo 1.2.1; the full library list and steps are in `firmware/FLASHING.md` of the `modified-blimpswarm` branch): FQBN
`esp32:esp32:XIAO_ESP32S3:USBMode=hwcdc,CDCOnBoot=default,FlashSize=8M,PartitionScheme=default_8MB,UploadSpeed=115200,PSRAM=disabled`,
`--library firmware`, sketch `firmware/examples/MultiRobotBicopter`.

Not included: flight logs `logs/`, `.venv`, build outputs, the toolchain, local `.bak` backups.
