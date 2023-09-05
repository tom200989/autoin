import autoit  # 用于操作指针的位置
import time
import threading
import keyboard
import pyautogui  # 用于获取真实鼠标的位置
from pynput import mouse

# 注意: 这里用到的一些概念
# 指针坐标: 是用户肉眼看到指针在屏幕的位置
# 鼠标坐标: 是真实鼠标通过传感器反馈给电脑的位置

# is_active = True
start_moving = False
lock_overtime = 5  # 锁屏超时时间(秒)
compose_key = 'alt+shift+ctrl+right'  # 快捷键

# 检测到鼠标点击时 - 停止自动移动
def on_click(x, y, button, pressed):
    global start_moving
    if pressed:
        start_moving = False

# 检测到鼠标滚动时 - 停止自动移动
def on_scroll(x, y, dx, dy):
    global start_moving
    start_moving = False

# 快捷键取反操作(激活:暂停:激活)
def toggle_activation_state(e=None):
    global is_active
    is_active = not is_active

# 自动移动指针逻辑
def move_mouse():
    global start_moving, is_active
    # 程序启动时, 获取初始化鼠标坐标以及初始化时间
    last_x, last_y = pyautogui.position()
    last_time = time.time()
    # 默认进入循环监测
    is_active = True
    # 默认不启动自动移动指针
    start_moving = False

    while True:
        # 如果进入循环监测
        print('is_activie = ', is_active)
        if is_active:
            # 获取当前鼠标坐标以及当前时间
            x, y = pyautogui.position()
            current_time = time.time()
            # 如果没有移动过鼠标
            if last_x == x and last_y == y:
                elapsed_time = current_time - last_time
                # 以及时间超出了规定的锁屏时间
                if elapsed_time >= lock_overtime:
                    # 则启动自动移动逻辑
                    start_moving = True
                # 自动逻辑生效中
                while start_moving and is_active:
                    # 往复移动鼠标
                    autoit.mouse_move(100, 100, speed=10)
                    time.sleep(0.2)  # 鼠标移动后立马获取一次真实鼠标坐标
                    x, y = pyautogui.position()
                    if x != 100 or y != 100:  # 检测到用户移动了鼠标
                        start_moving = False  # 立马退出自动移动逻辑

                    autoit.mouse_move(200, 200, speed=10)
                    time.sleep(0.2)
                    x, y = pyautogui.position()
                    if x != 200 or y != 200:
                        start_moving = False

                    last_x, last_y = x, y  # 把鼠标坐标缓冲到初始坐标变量
                    last_time = time.time()  # 把当前时间缓冲到初始时间变量

            else:  # 如果没有进入自动检测(比如用户按下了组合键 `ctrl + shift + alt + →`)
                last_x, last_y = x, y  # 把当前坐标作为初始坐标
                last_time = time.time()  # 把当前时间作为初始时间
                start_moving = False  # 立刻停止往复移动

            time.sleep(5)
        else:
            time.sleep(5)

if __name__ == '__main__':
    print('防自动锁屏程序开启!')
    # 创建两个新线程，一个用于移动鼠标，一个用于监听鼠标事件
    mouse_thread = threading.Thread(target=move_mouse)
    mouse_listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)

    # 使用add_hotkey来监听Alt+Shift+Ctrl+右方向键组合
    keyboard.add_hotkey(compose_key, toggle_activation_state)

    # 启动线程
    mouse_thread.start()
    mouse_listener.start()
    mouse_thread.join()
    mouse_listener.join()
