#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CLI="$PROJECT_DIR/.toolchain/bin/arduino-cli"
CONFIG="$PROJECT_DIR/.toolchain/arduino-cli.yaml"
FQBN="esp32:esp32:XIAO_ESP32S3:USBMode=hwcdc,CDCOnBoot=default,FlashSize=8M,PartitionScheme=default_8MB,UploadSpeed=115200,PSRAM=disabled"
FQBN_S3="esp32:esp32:esp32s3:USBMode=hwcdc,CDCOnBoot=cdc,FlashSize=8M,PartitionScheme=default,PSRAM=disabled"
usage() {
    cat <<'HELP'
Usage:
  ./firmware.sh ports                      list board serial ports
  ./firmware.sh build base                 build the base station (PC-side radio), ESP32-S3 boards only;
                                           for a plain ESP32 base see FLASHING.md section 4
  ./firmware.sh build robot                build the robot firmware
  ./firmware.sh upload base /dev/ttyACM0   build and flash the base station
  ./firmware.sh upload robot /dev/ttyACM0  build and flash the robot
  ./firmware.sh build nicla-test           build the Nicla serial test (prints the camera's 10 channels)
  ./firmware.sh upload nicla-test /dev/ttyACM0  build and flash the Nicla serial test to the robot board
  ./firmware.sh upload nicla-s3 /dev/ttyACM0    test the Nicla on a generic ESP32-S3 board (GPIO18 RX / GPIO17 TX)
  ./firmware.sh monitor /dev/ttyACM0       open a 115200-baud serial monitor
Default board: XIAO ESP32S3. Replace the port with the board actually connected.
This script needs the Arduino CLI toolchain in .toolchain/ next to it; see FLASHING.md for a plain arduino-cli setup.
HELP
}
[[ -x "$CLI" ]] || { echo 'Missing the Arduino CLI toolchain in .toolchain/ (see FLASHING.md).' >&2; exit 1; }
action="${1:-help}"
if [[ "$action" == ports ]]; then
    exec "$CLI" --config-file "$CONFIG" board list
elif [[ "$action" == monitor ]]; then
    [[ $# -eq 2 ]] || { usage; exit 2; }
    exec "$CLI" --config-file "$CONFIG" monitor -p "$2" --config baudrate=115200
elif [[ "$action" == help || "$action" == --help || "$action" == -h ]]; then
    usage
    exit 0
fi
[[ "$action" == build || "$action" == upload ]] || { usage; exit 2; }
[[ $# -ge 2 ]] || { usage; exit 2; }
target="$2"
case "$target" in
    base) sketch="$PROJECT_DIR/examples/BaseTranseiver" ;;
    robot) sketch="$PROJECT_DIR/examples/MultiRobotBicopter" ;;
    nicla-test) sketch="$PROJECT_DIR/examples/TestNicla" ;;
    nicla-s3) sketch="$PROJECT_DIR/examples/TestNiclaS3"; FQBN="$FQBN_S3" ;;
    *) usage; exit 2 ;;
esac
if [[ "$action" == upload ]]; then
    [[ $# -eq 3 && -c "$3" ]] || { echo 'Give a serial port that exists for the board.' >&2; exit 2; }
else
    [[ $# -eq 2 ]] || { usage; exit 2; }
fi
mkdir -p "$PROJECT_DIR/build/$target"
"$CLI" --config-file "$CONFIG" --no-color compile     --fqbn "$FQBN" --library "$PROJECT_DIR" --jobs 4     --build-path "$PROJECT_DIR/build/$target" "$sketch"     2>&1 | tee "$PROJECT_DIR/build/$target.log"
if [[ "$action" == upload ]]; then
    "$CLI" --config-file "$CONFIG" --no-color upload         --fqbn "$FQBN" --port "$3"         --input-dir "$PROJECT_DIR/build/$target" "$sketch"
fi
