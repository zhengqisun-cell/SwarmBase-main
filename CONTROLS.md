# SwarmBase Controls

SwarmBase is the ground-control program for the bicopter blimp. It reads an Xbox
controller and the keyboard, and sends commands through the base-station ESP32
(USB serial) to the robot over ESP-NOW. Press **H** in the dashboard window to show
or hide the quick reference below.

## Starting

```bash
.venv/bin/python RobotControl.py            # normal control (needs the Xbox controller)
.venv/bin/python RobotControl.py --monitor  # watch base connection and telemetry only
```

Before starting:

- The base station is plugged in; its port is `SERIAL_PORT` in `user_parameters.py`
  (currently `/dev/ttyUSB0`).
- The robot's MAC address is listed in `robot_macs` in `user_parameters.py`.
- The Xbox controller is connected.
- Click the dashboard window once so it receives key presses.

## Quick reference

<!-- quick-reference -->
```text
KEYBOARD (dashboard window focused)            XBOX CONTROLLER (selected robot)
  1-9 then Enter  select robot N                 B             Off -> Manual; any other -> Off
  0 then Enter    deselect                       A / X / Y     Auto / Balloon / Goal *
  s               stop: all robots, N s = one    Left stick    up / down = height
  b               autonomous balloon search      Right stick   left / right = yaw
  g               autonomous goal *              RT / LT       forward / backward
  c               calibrate sensors              LB / RB       no effect on this robot
  p               send preferences
  a / d           attacker / defender prefs    * The current robot firmware treats every
  y / o           yellow / orange prefs (avoid)  autonomous mode as balloon tracking.
  F1 / F2         track purple / green
  F3 / F4         track purple+green / red     Sticks have a 15% deadzone; releasing
  H               show / hide this help          them holds height and heading.
  Ctrl+C          quit (closing the window also quits)
```
<!-- /quick-reference -->

## Keyboard

Keys work only while the dashboard window has focus.

| Key | Action |
|---|---|
| `1`–`9`, then `Enter` | Select robot N (its position in `robot_macs`). The selected robot follows the controller and sends telemetry back. |
| `0`, then `Enter` | Deselect. The previously selected robot keeps its current mode. |
| `s` | Stop: switch to Off. With no number typed first it stops **all** robots; type a number first (`1` `s`) to stop one. |
| `b` | Autonomous balloon search (mode Auto). |
| `g` | Autonomous goal search. With the current firmware this also tracks balloons. |
| `c` | Ask the robot to calibrate its sensors. Keep it still. |
| `p` | Send the preferences in `Preferences.py` (the `FF:FF:FF:FF:FF:FF` block, then the robot's own block if it has one). |
| `a` / `d` | Send the attacker / defender preference sets. |
| `y` / `o` | Send the yellow / orange goal preference sets. **Avoid**: they are for goal mode, and `o` sets the camera frame to 160×120, which does not match the camera (240×160). |
| `F1` | Track purple balloons. |
| `F2` | Track green balloons. |
| `F3` | Track purple and green (locks onto one color at a time). |
| `F4` | Track red. |
| `H` | Show or hide the quick reference. |
| `Ctrl+C` | Quit. Closing the window also quits. |

Typing a number before a letter key applies that key to robot N only; without a number,
`s`, `b`, `g`, `c` and `p` are sent to all robots. `F1`–`F4` apply to the selected robot,
or to all robots when none is selected. The keys `f`, `[`, `]`, `=`, `-`, `;` and `'` drive
tensile follower robots and do nothing unless followers are configured.

## Xbox controller

Applies to the selected robot only.

| Input | Action |
|---|---|
| **B** | From Off: switch to Manual, keeping the current height and heading as targets. From Manual or any autonomous mode: switch to Off. The robot starts Off. |
| **A** | Auto mode (search, then track). |
| **X** | Balloon mode. |
| **Y** | Goal mode. With the current firmware this tracks balloons. |
| Left stick up/down | Raise / lower the height target. |
| Right stick left/right | Turn (yaw target). |
| Right trigger (RT) | Forward thrust. |
| Left trigger (LT) | Backward thrust. |
| LB / RB | Sent to the robot but not used by this robot type. |

Stick inputs below 15% and trigger inputs below 5% are ignored. Releasing the sticks
does not turn the robot off; it holds the current targets. Use **B** or `s` to stop.

## Robot modes

| Mode | Value | Behavior |
|---|---|---|
| Off | 0 | Motors idle. |
| Manual | 1 | Follows the controller with height and yaw feedback. |
| Auto | 2 | Searches (random walk); when the camera sees a target, moves to it. |
| Balloon | 3 | Same as Auto, balloon targets only. |
| Goal | 4 | Goal targets in the original project; balloons with the current firmware. |

## Balloon color

`F1`–`F4` choose what the camera tracks. The choice is sent with every control packet,
and the robot forwards it to the camera within about 0.2 s, then repeats it once a
second in case the camera restarts. Until a color key is pressed, the camera keeps its
own default (purple + green). The camera LED shows the locked color: magenta for
purple, green for green, red for red.

## Dashboard

| Element | Meaning |
|---|---|
| Battery | Robot battery voltage. |
| Yaw dial | Current heading (blue) and target heading (red). |
| Height bars | Current (Cur) and target (Des) height. |
| Camera box (right) | The camera frame; the purple square is the tracked target. Its size shows detection confidence, not the target's real size. Empty when nothing is detected. |
| Send Success | Always shown in this version; it is not a real link check. Use the telemetry age in status line 1 instead. |
| Status line 1 | Mode and motion being sent, selected color, and age of the last telemetry. |
| Status line 2 | Motor and servo commands reported by the robot over USB (only when the robot's USB is connected to this computer). |
| Status line 3 | Key hints, or a warning if logging fails. |

Telemetry (battery, heading, height, camera target) only arrives after a robot is
selected. Session logs are saved under `logs/`.

## Safety

- Test with propellers removed after any firmware or preference change.
- `s` with no number stops every robot; it is the fastest way to stop.
- Releasing the controller does not stop the robot.
