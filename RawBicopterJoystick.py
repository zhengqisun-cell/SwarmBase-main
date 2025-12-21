from comm.Serial import SerialController, DataType_Float
from input.JoystickManager import JoystickManager
from gui.simpleGUI import SimpleGUI
from user_parameters import ROBOT_MACS, SERIAL_PORT, PRINT_JOYSTICK
import pygame, time

ROBOT_MAC = ROBOT_MACS[0]

if __name__ == "__main__":
    serial = SerialController(SERIAL_PORT, timeout=.1)
    serial.manage_peer("A", ROBOT_MAC)
    serial.manage_peer("G", ROBOT_MAC)
    serial.send_preference(ROBOT_MAC, DataType_Float, "kpz", .6)
    serial.send_preference(ROBOT_MAC, DataType_Float, "kdz", .8)
    serial.send_control_params(ROBOT_MAC, (0,0,90,90,0,0,0,0,0,0,0,1,0))
    time.sleep(.2)

    joystick = JoystickManager()
    gui = SimpleGUI()

    # 初始化pygame窗口
    pygame.display.init()
    screen = pygame.display.set_mode((400, 260))
    pygame.display.set_caption("Control Monitor")
    font = pygame.font.SysFont("consolas", 20)
    clock = pygame.time.Clock()

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise KeyboardInterrupt

            axis, buttons = joystick.getJoystickInputs()
            if PRINT_JOYSTICK:
                print(" ".join(["{:.2f}".format(a) for a in axis]), buttons)

            # ================= 控制逻辑 =================
            # 左摇杆上下 (axis[0]) -> 总推力 throttle
            # 左摇杆左右 (axis[1]) -> 差动控制 turn
            throttle = (axis[0] + 1) / 2.0           # 0~1
            turn = axis[1]                           # -1(左) ~ +1(右)

            # 左右差动混合（turn 控制转向）
            # turn<0 左转：左快右慢；turn>0 右转：右快左慢
            m1 = throttle * (1 + turn)   # 左电机
            m2 = throttle * (1 - turn)   # 右电机

            # 限幅（防止超过 [0,1]）
            m1 = max(0.0, min(1.0, m1))
            m2 = max(0.0, min(1.0, m2))

            # 舵机：右摇杆控制两个方向翼
            s1 = (axis[2] + 1) * 90.0   # 上下
            s2 = (axis[3] + 1) * 90.0   # 左右
            led = axis[0]

            # ================= 读传感器 & GUI =================
            sensors = serial.getSensorData()
            if sensors:
                gui.update(cur_yaw=0, des_yaw=0, cur_height=sensors[0],
                           des_height=0, battery=0, distance=0, connection_status=True)

            # ================= 发送控制参数 =================
            serial.send_control_params(ROBOT_MAC, (m1, m2, s1, s2, led, 0,0,0,0,0,0,0,0))

            # ================= 显示状态 =================
            screen.fill((20,20,20))
            texts = [
                f"Throttle: {throttle:.2f}",
                f"Turn: {turn:+.2f}",
                f"M1: {m1:.2f}   M2: {m2:.2f}",
                f"S1: {s1:.1f}°  S2: {s2:.1f}°",
                f"LED: {led:.2f}",
                f"Sensors: {sensors[0]:.2f}" if sensors else "No sensors"
            ]
            for i,t in enumerate(texts):
                screen.blit(font.render(t, True, (255,255,0)), (10, 30*i+10))

            # 画推力条
            bar = int(throttle*200)
            pygame.draw.rect(screen,(0,180,0),(10,190,bar,20))
            pygame.draw.rect(screen,(200,200,200),(10,190,200,20),1)
            pygame.display.flip()
            clock.tick(50)

    except KeyboardInterrupt:
        print("Stopping!")
        serial.send_control_params(ROBOT_MAC,(0,0,90,90,0,0,0,0,0,0,0,0,0))
        serial.close()
        pygame.quit()
