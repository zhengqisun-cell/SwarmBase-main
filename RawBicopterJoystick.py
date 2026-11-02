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

    # Initialize the pygame window
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

            # ================= Control logic =================
            # Left stick up/down (axis[0]) -> total thrust (throttle)
            # Left stick left/right (axis[1]) -> differential (turn)
            throttle = (axis[0] + 1) / 2.0           # 0..1
            turn = axis[1]                           # -1 (left) .. +1 (right)

            # Left/right differential mix (turn steers)
            # turn < 0 turns left: left faster, right slower; turn > 0 turns right: right faster, left slower
            m1 = throttle * (1 + turn)   # left motor
            m2 = throttle * (1 - turn)   # right motor

            # Limit to [0, 1]
            m1 = max(0.0, min(1.0, m1))
            m2 = max(0.0, min(1.0, m2))

            # Servos: the right stick drives the two vanes
            s1 = (axis[2] + 1) * 90.0   # up/down
            s2 = (axis[3] + 1) * 90.0   # left/right
            led = axis[0]

            # ================= Read sensors & GUI =================
            sensors = serial.getSensorData()
            if sensors:
                gui.update(cur_yaw=0, des_yaw=0, cur_height=sensors[0],
                           des_height=0, battery=0, distance=0, connection_status=True)

            # ================= Send control parameters =================
            serial.send_control_params(ROBOT_MAC, (m1, m2, s1, s2, led, 0,0,0,0,0,0,0,0))

            # ================= Show status =================
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

            # Draw the thrust bar
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
