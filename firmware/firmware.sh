#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CLI="$PROJECT_DIR/.toolchain/bin/arduino-cli"
CONFIG="$PROJECT_DIR/.toolchain/arduino-cli.yaml"
FQBN="esp32:esp32:XIAO_ESP32S3:USBMode=hwcdc,CDCOnBoot=default,FlashSize=8M,PartitionScheme=default_8MB,UploadSpeed=115200,PSRAM=disabled"
FQBN_S3="esp32:esp32:esp32s3:USBMode=hwcdc,CDCOnBoot=cdc,FlashSize=8M,PartitionScheme=default,PSRAM=disabled"
usage() {
    cat <<'HELP'
用法：
  ./firmware.sh ports                      查看开发板串口
  ./firmware.sh build base                 编译电脑端无线基站
  ./firmware.sh build robot                编译机器人端
  ./firmware.sh upload base /dev/ttyACM0   编译并烧录基站
  ./firmware.sh upload robot /dev/ttyACM0  编译并烧录机器人
  ./firmware.sh build nicla-test           编译Nicla串口测试（打印相机10个通道）
  ./firmware.sh upload nicla-test /dev/ttyACM0  编译并烧录Nicla串口测试到机器人板
  ./firmware.sh upload nicla-s3 /dev/ttyACM0    在通用ESP32-S3板上测试Nicla（GPIO18收/GPIO17发）
  ./firmware.sh monitor /dev/ttyACM0       打开 115200 波特率串口监视器
默认开发板：XIAO ESP32S3。烧录端口须替换为当前连接的那一块板。
HELP
}
[[ -x "$CLI" ]] || { echo '缺少项目内的 Arduino CLI 工具链。' >&2; exit 1; }
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
    [[ $# -eq 3 && -c "$3" ]] || { echo '请指定实际存在的开发板串口。' >&2; exit 2; }
else
    [[ $# -eq 2 ]] || { usage; exit 2; }
fi
mkdir -p "$PROJECT_DIR/build/$target"
"$CLI" --config-file "$CONFIG" --no-color compile     --fqbn "$FQBN" --library "$PROJECT_DIR" --jobs 4     --build-path "$PROJECT_DIR/build/$target" "$sketch"     2>&1 | tee "$PROJECT_DIR/build/$target.log"
if [[ "$action" == upload ]]; then
    "$CLI" --config-file "$CONFIG" --no-color upload         --fqbn "$FQBN" --port "$3"         --input-dir "$PROJECT_DIR/build/$target" "$sketch"
fi
