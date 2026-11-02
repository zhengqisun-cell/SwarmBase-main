# SwarmBase

Branch `modified-blimpswarm`: the modified setup (as of 2026-11-02).

**Start with [firmware/FLASHING.md](firmware/FLASHING.md)**: build environment, flashing the robot and base station, ground-station setup, and checks before the first flight.

- Repository root: PC ground station (local modified version: controller mapping fix, flight logs, dashboard, Windows support); controls are described in `CONTROLS.md`.
- `firmware/`: modified BlimpSwarm robot firmware; see `firmware/MANUAL-FLIGHT-NOTES.md` (historical notes) and the source comments.

Main changes from the original project:
- Each motor's thrust and direction are computed from the same vector (the original paired them crosswise, which reversed the yaw torque once the forward part outweighed the lift); yaw tilt limit, and the yaw command is scaled down at high thrust (`yawAuthRef`).
- Selectable yaw-rate axis (`yawRateAxis=7`: the IMU is mounted on its side, so gyro y is the heading rate).
- Pitch compensation: zero captured automatically while Off, limited to ±25°.
- Downward thrust: up/down switch with hysteresis on the height error (`zDownErr`, `zDownMs`); the motors are cut while the servos flip (`zCoastMs`, `zSwingMs`); no more full-turn servo swings at ±180° when flying backward.
- Both motors at 55 Hz PWM, fixed 14-bit servo quantization, manual hold targets initialized from the sensors.
- IMU: the watchdog counts only polling time and no longer forces a re-initialization; the `softReset()` start-up sequence is restored.
- Telemetry health pages (attitude, outputs, health) and a USB execution log.

Not yet verified on the real robot: downward thrust hysteresis, and whether the IMU data stream stays continuous (attitude is read on a still bench on 2026-11-02, not yet confirmed while moving).

`Preferences.py` is set for this firmware: `pitchEn=True`, `botZlim=-0.5`; flash this firmware before pressing `p` to send them.

For building and flashing see `firmware/FLASHING.md`. On the author's machine `firmware/firmware.sh build robot` / `upload robot <port>` also works; that script uses `firmware/.toolchain` (Arduino ESP32 core 2.0.17, ESP32Servo 1.2.1, not included in the repository).

Not included: flight logs `logs/`, `.venv`, build outputs, the toolchain, local backups (`.bak`, `preserved/`), and the upstream `docs/`.
