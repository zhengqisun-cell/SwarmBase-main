# SwarmBase 手动控制补偿版使用说明

更新日期：2026-10-28。本文记录本机已完成的修改、使用方法和验证范围，以当前源码及截至2026-10-28的烧录、测试记录为依据。

## 1. 版本与目录

| 部分 | 本机位置 | 用途 |
|---|---|---|
| 手动控制补偿版固件 | [BlimpSwarm](/home/zhengqi-sun/Desktop/BlimpSwarm) | 本文主要说明的修改版 |
| 电脑端上位机 | [SwarmBase-main-main](/home/zhengqi-sun/Desktop/SwarmBase-main-main) | 读取Xbox手柄，通过通信板发送控制请求 |
| Print.h对照版固件 | [BlimpSwarm-PrintOnly](/home/zhengqi-sun/Desktop/BlimpSwarm-PrintOnly) | 基于原始源码，只补齐缺失的Print.h路径，用于版本对比 |
| 独立仿真 | [SwarmBase-MuJoCo](/home/zhengqi-sun/Desktop/SwarmBase-MuJoCo) | 手动控制、相机与ToF反馈、多气球路径测试 |

**最近一次已确认的硬件烧录状态（2026-10-28）：机器人板为PWM与翻转等待修复后的手动控制补偿版（ManualPlus），临时通信板仍为Print版（PrintFix）。** 补偿版源码和可恢复的应用镜像仍保留在本机；启动上位机不会自动切换板上固件。版本状态可查看[当前固件记录](/home/zhengqi-sun/Documents/Codex/2026-10-15/codex/work/active-firmware.json)。本文的硬件状态依据最近的烧录和检查记录更新。

电脑端手柄映射修正在两个固件版本之间共用。上次切换对照版时保留了板上参数，因此该对比主要改变固件实现。

**当前状态：PWM与翻转等待修复版已烧入机器人，冷启动后的断电台架检查通过；尚未验收带动力的机械效果。**

## 2. 控制链路与硬件

控制链路为：Xbox手柄 → 电脑端映射 → USB通信板 → ESP-NOW无线 → 机器人端手动行为 → PID与混控 → 输出补偿 → 电机和舵机。

电脑端负责发送操作请求；机器人ESP32执行飞控计算。PID控制形式和原有参数体系沿用项目，混控增加了数值保护，执行输出层加入了补偿。

| 设备 | 最近确认的型号／编译配置 | MAC地址 | 最近确认的串口 |
|---|---|---|---|
| 机器人控制板 | ESP32-S3、8MB闪存；使用XIAO_ESP32S3配置 | `48:27:E2:E6:E6:44` | `/dev/ttyACM0` |
| 临时通信板 | 普通ESP32、4MB闪存；使用ESP32 Dev Module配置 | `A4:F0:0F:76:DF:AC` | `/dev/ttyUSB0` |

串口编号可能随连接顺序变化。上位机的串口应填写**通信板**的串口；机器人USB主要用于烧录和日志检查。

补偿版机器人代码中的接口标号：舵机1为`D0`，舵机2为`D1`，电机1为`D9`，电机2为`D10`。这里是开发板的D口标号。

## 3. 已完成的修改

| 修改 | 具体行为 | 主要文件 |
|---|---|---|
| Print.h路径补齐 | 将原文件复制到`src/util/Print.h`，使示例的包含路径可用 | `src/util/Print.h` |
| 手柄松手输入修正 | 扳机从`-1..1`归一化到`0..1`，设置松开死区，再计算前后请求 | 上位机`robot/RobotMaster.py` |
| 舵机方向数值保护 | 使用向量模长、`atan2`计算方向；推力方向过小时保留有效历史角度，首次无历史时使用默认角度 | `src/robot/FullBicopter.cpp`、`.h` |
| 电机频率统一 | 两路电机都设置为55Hz；舵机保持50Hz | `src/robot/RawBicopter.cpp` |
| 舵机PWM稳定量化 | 舵机使用14位固定脉宽量化，取消相邻占空比轮换 | `src/act/AServo.cpp`、`.h` |
| 大幅翻转保护 | 两路电机先回最低输出，再锁定舵角等待，之后允许恢复推力 | `src/act/ServoFlipGuard.h`、`src/robot/RawBicopter.cpp` |
| 手动保持目标初始化 | 首次使用和停机时，从传感器初始化保持高度和航向 | `src/state/nicla/ManualState.cpp`、`.h` |
| 收发及输出日志 | 关联收到的命令、行为输出、执行器请求、PWM库设置和LEDC寄存器读数 | `examples/MultiRobotBicopter/MultiRobotBicopter.ino`及执行器文件 |

### 3.1 舵机PWM补偿

保留原有的整数角度到整数微秒映射。舵机改为50Hz、14位PWM，将目标脉宽取最近可用刻度；同一角度始终输出同一刻度，不再通过相邻占空比轮换补偿平均误差。每刻度约1.22微秒。电机仍使用55Hz、10位PWM，没有修改ESP32Servo库。

端点仍遵守原库的限幅；控制循环迟到时不补发一串写入，并记录迟到帧数。该机制补偿的是软件量化误差，不是舵机机械零位或电机推力标定。

### 3.2 翻转保护

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `TRIGGER_DEG` | 100° | 按`servoRange`换算后的最大角度命令变化阈值 |
| `COAST_US` | 650000微秒 | 两路电机回最低输出、保持原舵机命令的等待时间 |
| `SETTLE_US` | 350000微秒 | 锁定一次舵角命令的等待时间 |

流程：正常输出 → 检测到大幅翻转 → 两路电机最低输出并保持原舵角650毫秒 → 下发并锁定一次舵角350毫秒 → 允许恢复电机输出。等待中小幅目标变化不移动已锁定的舵角，也不重置计时；等待结束时若最新目标又超过100°翻转阈值，则继续保持两路电机最低输出，锁定新目标后重新等待350毫秒。首次进入输出层也先经过锁定等待；停机请求的电机输出始终保持为零。

**硬件没有电机转速／推力反馈或舵机轴角反馈。** 上述条件使用的是角度命令差和计时等待，不表示已经测到电机停转或舵机到位。650／350毫秒尚未通过本机带载测量标定。

## 4. 启动上位机与手柄操作

先确认通信板、Xbox手柄已连接，且没有其他程序占用基站串口。连接配置在[user_parameters.py](/home/zhengqi-sun/Desktop/SwarmBase-main-main/user_parameters.py)中：

```python
robot_macs = ["48:27:E2:E6:E6:44"]
SERIAL_PORT = "/dev/ttyUSB0"
```

正式手柄入口：

```bash
cd /home/zhengqi-sun/Desktop/SwarmBase-main-main
.venv/bin/python RobotControl.py
```

不需要`--joystick`后缀。只监视基站与缓存遥测、无需手柄时使用：

```bash
.venv/bin/python RobotControl.py --monitor
```

### 4.1 手柄映射

| 操作 | 当前用途 |
|---|---|
| 左摇杆上下 | 请求升高／降低 |
| 右摇杆左右 | 请求偏航转向 |
| RT右扳机 | 请求前进 |
| LT左扳机 | 请求后退；与RT同时按时，两者相减 |
| B | 停机与手动运行之间切换 |
| A | 原项目自主状态机 |
| X | 原项目气球模式 |
| Y | 原项目目标模式 |
| LB／RB | 辅助通道；当前双电机机型未使用 |
| 左摇杆左右、右摇杆上下 | 当前未用于控制 |
| 十字键、菜单键、视图键、摇杆按下等 | 当前程序未绑定 |

摇杆死区为15%，扳机松开死区为5%。松手表示运动请求归零，运行状态不会随之关闭；仍可能存在高度或姿态保持输出。A／X／Y属于原项目自主功能，不是下文的仿真多气球路径流程，也不在本次手动补偿版的自主飞行验收范围内。

### 4.2 常用键盘操作

键盘输入由上位机图窗接收，操作前先点击图窗。

| 输入 | 用途 |
|---|---|
| `1`再按Enter | 选择1号机器人 |
| `s` | 发送停机；不带编号时对全部机器人操作 |
| `1`再按`s` | 针对1号机器人发送停机 |
| `p` | 上传本地参数配置 |
| 小写`b`／`g` | 原项目自主气球／目标入口 |
| `c` | 设置电调校准标志；本次工作没有执行校准 |

手柄B和键盘小写`b`功能不同。编号选择和启停都会发送板端命令；只查看连接时使用`--monitor`。做固件对比时，保持参数和手柄映射一致；`p`是参数上传操作，不是启动开关。

## 5. 参数与日志

参数保存在机器人非易失性存储区（NVS）中，本次应用区烧录保留了这些参数。电脑端[Preferences.py](/home/zhengqi-sun/Desktop/SwarmBase-main-main/Preferences.py)保存可上传的配置，并不代表每次启动都会自动覆盖板上全部参数。

常用参数：`zEn`／`yawEn`为高度／航向反馈开关；`kpz`／`kdz`／`kiz`为高度PID参数；`lx`为电机半间距；`servoRange`／`servoBeta`为舵机映射参数。修改配置后需明确执行参数上传才会应用到板上。

补偿版串口日志使用115200波特率：

| 字段 | 含义 |
|---|---|
| `[CMD]`、`seq` | 收到的命令及关联序号 |
| `[CFG]` | 当前飞控参数快照 |
| `[EXEC]`、`beh` | 执行快照及状态机给出的行为向量 |
| `requested`／`out` | 补偿前请求／补偿后执行器输出向量 |
| `flip_phase` | 0正常、1停推力等待、2转舵等待 |
| `pwm_updates`／`pwm_late` | 舵机PWM更新数／迟到帧数 |
| `servo_ticks_set` | 最新写入的舵机PWM整数刻度 |
| `servo_tick_sum`／`servo_us_sum` | 累计写入刻度／累计期望脉宽，用于检查软件平均误差 |
| `ledc1`至`ledc4` | 引脚、通道、分辨率、频率、当前周期占空比读数 |

这些日志是软件设置和寄存器读回，不是实际推力、转速、轴角或外部波形测量。Print.h对照版没有这些新增输出日志。

## 6. 编译配置

本机工具链为Arduino ESP32核心2.0.17、ESP32Servo 1.2.1，位于补偿版目录的`.toolchain`下。

编译补偿版机器人：

```bash
cd /home/zhengqi-sun/Desktop/BlimpSwarm
./firmware.sh build robot
```

`firmware.sh`默认使用XIAO_ESP32S3配置，`build base`也生成ESP32-S3基站版本。当前临时通信板为普通ESP32，编译它应使用对应配置：

```bash
cd /home/zhengqi-sun/Desktop/BlimpSwarm
.toolchain/bin/arduino-cli --config-file .toolchain/arduino-cli.yaml compile \
  --fqbn 'esp32:esp32:esp32:FlashSize=4M,PartitionScheme=default,FlashMode=dio,FlashFreq=40,UploadSpeed=115200,PSRAM=disabled' \
  --library "$PWD" --jobs 4 --build-path "$PWD/build/base-esp32-test" \
  "$PWD/examples/BaseTranseiver"
```

以上均只编译。两种芯片的基站镜像不能混用；ESP32-S3基站源码和产物仍保留在项目中。

## 7. 已完成的验证

下表为本次输出修复前的历史记录；当前候选的验证见第12节。

| 层次 | 已验证内容 | 证据 |
|---|---|---|
| 离线C++ | 实际修改源码及ESP32Servo库，在模拟GPIO／LEDC和时钟下测试；含10万组保护状态输入、启停、途中改目标、异常值和32位计时溢出 | [离线测试记录](/home/zhengqi-sun/Documents/Codex/2026-10-15/codex/outputs/manual-compensation-offline-tests.json) |
| PWM软件统计 | 1000次名义50Hz更新，两侧平均脉宽误差均小于0.02微秒；限幅、迟到帧和50／55Hz设置通过 | 同上 |
| 补偿版硬件停机检查 | 35条输出快照，电机55Hz、舵机50Hz、软件PWM累计误差和12次停机无线遥测通过 | [硬件检查记录](/home/zhengqi-sun/Documents/Codex/2026-10-15/codex/outputs/manual-compensated-hardware.json) |
| 移植保护的物理仿真 | 悬停、升降、转向各70秒；90%浮力模型中未触地，最大水平位移小于0.5毫米，升降最低高度约0.44米 | [仿真检查记录](/home/zhengqi-sun/Documents/Codex/2026-10-15/codex/outputs/manual-ported-guard-mujoco.json) |
| Print.h对照版 | 机器人和普通ESP32通信板均烧录校验通过；冷启动后有姿态数据，12次停机遥测通过 | [对照版检查记录](/home/zhengqi-sun/Documents/Codex/2026-10-15/codex/outputs/print-only-stopped-hardware.json) |

补偿版当次热复位后的姿态字段全零；之后切换到Print.h对照版并冷启动，姿态数据恢复。这两次结果分别记录，不能把对照版冷启动检查当作补偿版的冷启动验收。

仿真采用120克质量、90%浮力以及尚未实测识别的动力学参数。带载波形、电机转速、舵机机械运动和自由飞行尚未验收。先前固定1秒＋1秒的等待方案未通过升降仿真，当前保留的版本为650＋350毫秒。

## 8. 备份与恢复补偿版

最近一次切换对照版前的[留档目录](/home/zhengqi-sun/Desktop/BlimpSwarm-backups/before-print-only-both-boards-20261027-183121)包含：

| 文件 | 内容 |
|---|---|
| `compensated-source.tar.gz` | 补偿版源码 |
| `robot-current-application-at-0x10000.bin` | 从机器人板实时读回、与已校验补偿镜像一致的应用程序 |
| `robot-current-prefix-and-application.bin` | 机器人0x0至0xD0000，覆盖引导、分区、参数、OTA数据和当时应用；并非整片8MB镜像 |
| `base-current-full-flash.bin` | 临时通信板的完整4MB闪存 |
| `base-current-application-at-0x10000.bin` | 临时通信板应用副本 |
| `manifest.json`、`恢复及运行说明.txt` | 校验值、烧录记录及恢复说明 |

需要回到已验证烧录的补偿镜像时，先断开电调动力和舵机供电，关闭串口占用程序，核对机器人身份及分区布局，再只恢复机器人应用：

```bash
cd /home/zhengqi-sun/Desktop/BlimpSwarm
python3 .toolchain/data/packages/esp32/tools/esptool_py/4.5.1/esptool.py \
  --chip esp32s3 \
  --port '/dev/serial/by-id/usb-Espressif_USB_JTAG_serial_debug_unit_48:27:E2:E6:E6:44-if00' \
  --baud 460800 write_flash \
  --flash_mode keep --flash_freq keep --flash_size keep --verify --no-progress \
  0x10000 '/home/zhengqi-sun/Desktop/BlimpSwarm-backups/before-print-only-both-boards-20261027-183121/robot-current-application-at-0x10000.bin'
```

此命令会写入硬件，仅在明确决定切回补偿版时执行。通信板本身没有机器人输出补偿逻辑，切回补偿版机器人时通常可以继续使用已匹配的通信板程序。恢复后先检查启动日志和停机遥测，再安排带载测试；上述恢复命令没有在本次文档编写中执行。

更早的[补偿版开发留档](/home/zhengqi-sun/Desktop/BlimpSwarm-backups/manual-flight-20261027-162608)还保存了修改前源码、当时的旧8MB闪存，以及补偿应用和测试封存文件。

## 9. 独立仿真入口

多气球自主跟踪位于独立MuJoCo工程，未随手动固件烧入真机：

```bash
cd /home/zhengqi-sun/Desktop/SwarmBase-MuJoCo
python3 sim.py --viewer --balloon-path
```

点击窗口后，小键盘`.`复位、Enter开始、`0`停机。四只气球静止且逐个变绿；机器人仅从图像持续缺失判断丢失目标，0.3秒后搜索，再通过相机与ToF反馈靠近并保持约80%画面占比。稳定3秒后场景激活下一只，不向控制器发送换目标通知。

[窗口测试记录](/home/zhengqi-sun/Desktop/SwarmBase-MuJoCo/outputs/balloon-path-native-window-test.json)约112.8秒完成四点，最终稳定段占比约77.6%～82.4%。这些结果仅属于仿真，不代表真机已具备该自主流程。

## 10. 最近一次恢复记录（2026-10-28）

机器人已从Print版恢复为此前校验的ManualPlus应用，通信板未刷写。机器人原应用和参数／引导区已[实时留档](/home/zhengqi-sun/Desktop/BlimpSwarm-backups/before-ManualPlus-restore-20261028-135417)；应用烧录校验通过，前64KB与恢复前逐字节一致。USB冷启动后的[停机复查](/home/zhengqi-sun/Documents/Codex/2026-10-15/codex/outputs/ManualPlus-restored-20261028.json)通过：34条输出快照、两路电机55Hz／舵机50Hz、PWM累计值和12次无线遥测正常，已读到非零姿态数据。没有发送运动请求或写入参数；尚未验证带载飞行及实物转速／舵机轴角。

## 11. 手动控制诊断界面（2026-10-28）

启动命令保持不变。界面沿用原版航向盘、高度条、电量、距离、视觉框和滑块，原控件尺寸与交互保留；只在底部增加三行状态，显示电脑模式和发送动作、回传时间、板端电机／舵机输出及日志状态。原先多栏诊断面板和推力曲线已从默认界面移除；详细收发数据、PWM计数和翻转保护记录仍保存在日志文件。

通信板仍使用原来的无线协议。机器人详细输出来自可选的机器人USB日志口（115200波特率），由`user_parameters.py`中的`ROBOT_LOG_PORT`和`ROBOT_LOG_MAC`指定；只被动读取，不写机器人USB或主动复位。机器人USB缺失时手柄通信仍使用基站，界面明确显示缺失数据；超过3秒未收到的板端数据会标记过期。不要同时使用其他程序占用机器人日志口。

每次启动自动将带UTC时间、会话相对时间的输入、完整13参数、已发送控制包、基站响应、遥测和机器人日志写入上位机目录下的`logs/时间戳/session.jsonl`。电脑串口写出不代表无线已送达；基站遥测是缓存，不能证明机器人采样时间。重复指令的内容匹配不构成逐包唯一确认。板端日志表示软件尝试执行的输出；尚无电机转速、实物舵机角度或真实前进速度反馈。先按`s`停机，关闭图窗不能代替停机。

本次仅修改电脑端界面和观测／日志功能，未修改固件或手柄映射。离线新旧参数对比501组通过；控制包逐字节对比、伪串口、断连／过期、日志写入失败和界面渲染验证通过，尚未实机联调。

## 12. PWM与翻转等待修复（2026-10-28，离线阶段记录）

当前源码仅更新`src/act/AServo.cpp`、`AServo.h`和`ServoFlipGuard.h`，手柄映射、PID／参数、混控和上位机界面未改。修改前的133个文件与最近已验证旧应用镜像已[留档](/home/zhengqi-sun/Desktop/BlimpSwarm-backups/before-pwm-guard-fix-20261028-144925)；旧应用是复制此前读回并校验的镜像，本轮未重新读取闪存。

[离线测试](/home/zhengqi-sun/Documents/Codex/2026-10-15/codex/outputs/pwm-guard-fix-offline-tests-20261028.json)编译了实际执行器源码与ESP32Servo库，硬件调用由桩替代：固定角度1000帧无脉宽轮换、全部181个整数角度各25帧稳定，量化误差最大约0.607微秒；舵机14位／50Hz与电机10位／55Hz隔离通过。锁定等待、噪声下恢复、再次大幅反向、停机、非法输入、32位计时回绕与10万组随机测试通过，并启用地址及未定义行为检查。

台架2Hz请求样本的稀疏回放中，前进／后退均能恢复非零输出。另用相同样本线性插值到250Hz，并让新旧保护从共同的锁定等待状态开始比较；该插值回放是构造测试，不能作为原台架全部控制周期或真实硬件效果的复现。

ESP32-S3候选固件[编译通过](/home/zhengqi-sun/Documents/Codex/2026-10-15/codex/outputs/pwm-guard-fix-robot-build-20261028.json)；该离线阶段未烧录、未连接串口、未发送任何命令，之后的上板结果见第13节。该修复仅消除固定角度下PWM轮换及小幅目标变化造成的无限等待；高度反馈本身的角度变化、实物抖动与转速差尚未实机验收。650／350毫秒仍是未带载标定的等待参数。

## 13. 修复版烧录与断电台架检查（2026-10-28）

已只写入机器人`0x10000`应用区并通过镜像校验，原前64KB引导／分区／参数／OTA区域与写入前逐字节一致，通信板未写。烧录前的旧应用已[实时备份](/home/zhengqi-sun/Desktop/BlimpSwarm-backups/before-fixed-pwm-guard-flash-20261028-150203)；不是8MB整片备份。

用户确认保持电调动力和舵机供电断开，仅通过USB供电，并在热复位姿态全零后完成机器人USB冷启动。[本轮检查](/home/zhengqi-sun/Documents/Codex/2026-10-15/codex/outputs/fixed-pwm-guard-hardware-summary-20261028.json)通过：固定135°／45°命令的两路PWM刻度稳定为1618／840，软件库微秒读数为1975／1025，LEDC占空比寄存器与设置一致，舵机14位／50Hz和电机55Hz符合预期；未用示波器测量物理引脚波形。

停机、松手、上升、释放上升、下降、前进、后退、最终停机共8组请求均与板端接收值逐位一致，每组取得8条关联输出快照。升降和前后均恢复非零最终输出；RUN阶段的电机输出与计算请求一致，COAST／SETTLE阶段两路均为零，最后的清理停机已确认收到并执行。本轮未写入参数，也未测试实际转速、实物舵机轴角或自由飞行。

保持模式仍会因高度等反馈改变舵角，部分片段仍触发短暂保护停推；因此本轮通过表示固定角度PWM不再轮换、四方向不再持续卡住，并不表示所有机械抽搐和转速差都已消失。无线回传遥测未在本轮重新查询，收发对照采用无线CMD与机器人USB输出日志。
