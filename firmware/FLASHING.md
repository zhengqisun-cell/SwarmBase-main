# 固件编译与烧录指南（modified-blimpswarm 分支）

本指南把 `firmware/` 里的固件烧进机器人，并完成第一次上电前的配置。
以下命令都在**仓库根目录**（含 `RobotControl.py` 和 `firmware/` 的目录）执行。

## 0. 硬件一览

| 板子 | 芯片 | 用途 | 需要烧的程序 |
|---|---|---|---|
| 机器人控制板 | Seeed XIAO ESP32S3（8MB） | 飞控，接电机、舵机、IMU、气压计、相机 | `firmware/examples/MultiRobotBicopter` |
| 基站（通信板） | 普通 ESP32（4MB）或 ESP32-S3 | 插电脑 USB，与机器人走 ESP-NOW 无线 | `firmware/examples/BaseTranseiver` |

**基站一般不用重烧**：本分支的基站程序与原版完全相同；拿到的基站能用就跳过第 4 节。

> ⚠️ 烧录、校准和台架测试时**一律拆掉螺旋桨**。

## 1. 安装编译环境（只需一次）

版本要与下表一致，这是本固件实际编译、上机使用的版本。

| 组件 | 版本 |
|---|---|
| arduino-cli | 1.x（测试用 1.5.1） |
| Arduino ESP32 核心 `esp32:esp32` | **2.0.17**（不要用 3.x） |
| ESP32Servo | 1.2.1 |
| SparkFun BNO08x Cortex Based IMU | 1.0.6 |
| Adafruit BMP3XX Library | 2.1.6 |
| Adafruit BusIO | 1.17.4 |
| Adafruit Unified Sensor | 1.1.15 |
| IBusBM | 1.1.4 |

安装 arduino-cli：见 <https://arduino.github.io/arduino-cli/latest/installation/>（Windows 下载 zip 解压后把目录加入 PATH）。然后：

```bash
arduino-cli config init
arduino-cli config add board_manager.additional_urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
arduino-cli core update-index
arduino-cli core install esp32:esp32@2.0.17
arduino-cli lib install "ESP32Servo@1.2.1" "SparkFun BNO08x Cortex Based IMU@1.0.6" "Adafruit BMP3XX Library@2.1.6" "Adafruit BusIO@1.17.4" "Adafruit Unified Sensor@1.1.15" "IBusBM@1.1.4"
```

Linux 用户还需把自己加入串口组，然后重新登录：`sudo usermod -aG dialout $USER`。

> 使用 Arduino IDE 也可以：开发板管理器装 esp32 2.0.17，库管理器按上表版本装库，把 `firmware` 文件夹复制到 Arduino 的 `libraries/` 下并命名为 `BlimpSwarm`，开发板选 "XIAO_ESP32S3"，选项与下面的 FQBN 一致。

## 2. 找到串口

```bash
arduino-cli board list
```

- 机器人：USB 接 XIAO 板，Linux 上一般是 `/dev/ttyACM0`，Windows 上是 `COMx`（"USB JTAG/serial debug unit"）。
- 基站：Linux 上一般是 `/dev/ttyUSB0`，Windows 上是 `COMx`（CH340/CP210x）。

下面用 `<机器人串口>`、`<基站串口>` 代替，换成实际名字。

## 3. 编译并烧录机器人

```bash
arduino-cli compile --fqbn "esp32:esp32:XIAO_ESP32S3:USBMode=hwcdc,CDCOnBoot=default,FlashSize=8M,PartitionScheme=default_8MB,UploadSpeed=115200,PSRAM=disabled" --library firmware --build-path build/robot firmware/examples/MultiRobotBicopter
```

成功时最后打印 `Sketch uses 776109 bytes (23%) ...`（数字可能略有出入）。

```bash
arduino-cli upload --fqbn "esp32:esp32:XIAO_ESP32S3:USBMode=hwcdc,CDCOnBoot=default,FlashSize=8M,PartitionScheme=default_8MB,UploadSpeed=115200,PSRAM=disabled" --input-dir build/robot --port <机器人串口> firmware/examples/MultiRobotBicopter
```

成功时每段都显示 `Hash of data verified.`。烧录**不会清除**板上已保存的参数（NVS）。

烧录不上时：按住板上 **B（BOOT）键**，插上 USB，再松开，然后重新执行 upload。

## 4. （需要时）编译并烧录基站

普通 ESP32 基站：

```bash
arduino-cli compile --fqbn "esp32:esp32:esp32:FlashSize=4M,PartitionScheme=default,FlashMode=dio,FlashFreq=40,UploadSpeed=115200,PSRAM=disabled" --library firmware --build-path build/base-esp32 firmware/examples/BaseTranseiver
arduino-cli upload --fqbn "esp32:esp32:esp32:FlashSize=4M,PartitionScheme=default,FlashMode=dio,FlashFreq=40,UploadSpeed=115200,PSRAM=disabled" --input-dir build/base-esp32 --port <基站串口> firmware/examples/BaseTranseiver
```

ESP32-S3 基站：把两条命令里的 FQBN 换成第 3 节机器人的 FQBN，`build/base-esp32` 换成 `build/base-s3`。
**两种芯片的程序不能混用**，先确认基站是哪种芯片。

## 5. 检查机器人开机日志

```bash
arduino-cli monitor -p <机器人串口> -c baudrate=115200
```

（打开串口会让机器人重启一次，这是正常的；`Ctrl+C` 退出。）正常应看到：

```
Start!
ESP Board MAC Address:  48:27:E2:E6:E6:44      ← 记下这个 MAC
BNO Initialization!
  BNO started: 1
Sensor was reset
Setting desired reports
Gryo Integrated Rotation vector enabled
...
```

- 出现 `Ooops, no BNO085 detected`，或一直没有 `Sensor was reset`：**拔掉 USB 和电池，等 10 秒再上电**（IMU 卡住后只有彻底断电才能恢复），再检查一次。仍不行再查 IMU 的 I2C 接线。
- 出现 `Main Base Not Set.`：新机器人还没记住基站，第 6 节启动地面站后会自动配对；若仍收不到遥测，给机器人重新上电一次。

## 6. 配置地面站并下发参数

地面站可在 Linux、macOS、Windows 上运行。Windows 上不读取机器人 USB 日志（`ROBOT_LOG_PORT` 会被忽略，仪表盘显示 "Robot USB log not supported on this OS"），无线控制和地面站日志 `logs/` 不受影响。

1. 安装 Python 依赖（在仓库根目录；测试环境：Python 3.12、pyserial 3.5、pygame 2.6.1、matplotlib 3.6.3、numpy 1.26.4）：
   ```bash
   sudo apt install python3-tk        # Ubuntu/Debian：仪表盘窗口需要
   python3 -m venv .venv
   .venv/bin/pip install pyserial pygame matplotlib numpy
   ```
   Windows（安装 Python 时勾选 tcl/tk，默认就有）：
   ```bat
   python -m venv .venv
   .venv\Scripts\python -m pip install pyserial pygame matplotlib numpy
   ```
2. 编辑 `user_parameters.py`：
   - `robot_macs = ["<第 5 节记下的 MAC>"]`
   - `SERIAL_PORT = "<基站串口>"`（Windows 上形如 `"COM5"`）
   - `ROBOT_LOG_PORT`：机器人 USB 日志口（可选，只用于记录日志）；不用时可保持原样，找不到会自动跳过。
3. 接上 Xbox 手柄，启动：
   ```bash
   .venv/bin/python RobotControl.py
   ```
   Windows：`.venv\Scripts\python RobotControl.py`
4. 点一下仪表盘窗口，按 `1` 再按 `Enter` 选中机器人，再按 **`p` 下发参数**。
   `Preferences.py` 是按本固件设置的（`pitchEn=True`、`botZlim=-0.5` 等），**必须先烧好本固件再按 `p`**，旧固件收到这些参数会出问题。

操作说明见仓库根目录的 `CONTROLS.md`。

## 7. 第一次上电前的检查（拆桨）

1. **电调行程校准**（新电调、换过电调时必须做）：选中机器人后按 `1` 再按 `c`，然后拔掉 USB 和电池彻底断电，再上电。上电后电机**不会转**，两个电调会在高点、低点各响一组提示音，约 20 秒结束。之后再断电、上电一次，确认不会再进入校准。
2. 手柄 **B** 进入手动模式：两个舵机朝上。
3. 慢慢推左摇杆向上：两个电机应同时起转；高油门时两边声音应一致（不一致先查电调）。
4. 按 **RT**：两个舵机朝同一方向前倾（前进）；推右摇杆左右：两个舵机一前一后反向倾斜。
5. 手拿机器人慢慢左右转动：仪表盘的航向表盘应跟着转（IMU 正常）。
6. 键盘 `s` 或手柄 **B** 停机。

全部正常后再装桨，低空、每次只做一个动作地试飞。飞行日志保存在 `logs/`。

## 8. 回退到原版固件

本仓库 `robot-printonly` 分支的 `firmware/` 是原版固件（仅补了 `Print.h`），编译烧录命令相同。注意该分支的 `Preferences.py` 不同（`pitchEn=False`、`botZlim=0`），回退时地面站也要一起切换分支。

## 已知限制

- Windows 上不记录机器人 USB 日志（见第 6 节）。
- Xbox 手柄的原始轴编号在 Windows 和 Linux 上不同，`input/JoystickManager.py` 按系统自动选择（Linux 已实测；Windows 按 pygame 文档的 XInput 顺序：右摇杆 2/3、LT 4、RT 5）。macOS 沿用 Linux 编号，未测试。
- Windows 支持是在 Linux 上模拟验证的，**尚未在真实 Windows 电脑上跑过**。在 Windows 上第一次使用时，拆桨、进入手动模式，逐个操作摇杆和扳机，确认第 7 节第 3、4 步的舵机/电机反应正确；松开所有摇杆扳机时不应有任何动作。

## 尚未经实机验证

- 向下推力回差（`zDownErr` 等）：仿真通过，未实飞。
- IMU 数据流能否持续：静置台架上能读到姿态，转动状态下尚未确认（第 7 节第 5 步就是这项检查）。
