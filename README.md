# SwarmBase

本分支 `robot-printonly`：2026-11-02 机器人上实际运行的组合。

- 根目录：电脑端地面站（本地修改版：手柄映射修正、飞行日志、仪表盘），操作说明见 `CONTROLS.md`。
- `firmware/`：机器人固件 BlimpSwarm-PrintOnly，即原项目源码，只补了 `src/util/Print.h`。

注意（这套固件的已知行为）：
- `fx` 在固件里取反：手柄 **RT 往后、LT 往前**。
- 偏航环用陀螺 z 轴，这台机器人 IMU 侧装，z 轴实为左右摆动。
- 两路电机 PWM 为 55 Hz / 58 Hz。
- `Preferences.py` 已按此固件设置：`pitchEn=False`（固件直接加 IMU 原始角，侧装约 +90°），`botZlim=0`（无上下回差）。
- 烧录后 ESP 单独复位时找不到 IMU，需拔掉 USB 和电池彻底断电。

编译烧录（需 Arduino ESP32 核心 2.0.17、ESP32Servo 1.2.1）：FQBN
`esp32:esp32:XIAO_ESP32S3:USBMode=hwcdc,CDCOnBoot=default,FlashSize=8M,PartitionScheme=default_8MB,UploadSpeed=115200,PSRAM=disabled`，
`--library firmware`，草图 `firmware/examples/MultiRobotBicopter`。

未包含：飞行日志 `logs/`、`.venv`、编译产物、工具链、本地 `.bak` 备份。
