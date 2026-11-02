# SwarmBase

本分支 `modified-blimpswarm`：改版组合（截至 2026-11-02）。

**上手请先看 [firmware/FLASHING.md](firmware/FLASHING.md)**：编译环境、烧录机器人与基站、地面站配置、第一次上电检查。

- 根目录：电脑端地面站（本地修改版：手柄映射修正、飞行日志、仪表盘），操作说明见 `CONTROLS.md`。
- `firmware/`：机器人固件 BlimpSwarm 修改版，修改记录见 `firmware/MANUAL-FLIGHT-NOTES.md` 和源码注释。

主要修改（相对原项目）：
- 推力幅值与方向成对计算（原版交叉配对，前进分量大时偏航力矩反向）；偏航倾角上限，高推力时缩小偏航指令（`yawAuthRef`）。
- 偏航角速度轴可选（`yawRateAxis=7`：IMU 侧装，陀螺 y 为航向角速度）。
- 俯仰补偿：停机时自动取零点，限制 ±25°。
- 向下推力：按高度误差加回差（`zDownErr`、`zDownMs`），翻转时先断推力（`zCoastMs`、`zSwingMs`）；后退时舵机不再在 ±180° 处整圈甩动。
- 两路电机 PWM 统一 55 Hz，舵机 14 位固定量化，手动模式保持目标初始化。
- IMU：看门狗只计读取时间、不再强制重新初始化；恢复 `softReset()` 启动流程。
- 遥测健康页（姿态、输出、健康）和 USB 执行日志。

未经实机验证：向下推力回差、IMU 数据流能否持续（2026-11-02 静置台架上能读到姿态，未在转动下确认）。

`Preferences.py` 已按此固件设置：`pitchEn=True`、`botZlim=-0.5`；必须先烧录本固件再按 `p` 下发。

编译烧录见 `firmware/FLASHING.md`。本机也可用 `firmware/firmware.sh build robot` / `upload robot <串口>`，该脚本使用 `firmware/.toolchain`（Arduino ESP32 核心 2.0.17、ESP32Servo 1.2.1，未包含在仓库中）。

未包含：飞行日志 `logs/`、`.venv`、编译产物、工具链、本地备份（`.bak`、`preserved/`）、上游 `docs/`。
