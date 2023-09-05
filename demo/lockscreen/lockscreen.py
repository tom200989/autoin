import ctypes
import os
import sys
import autoit
import time
import threading
import keyboard
import pyautogui
from pynput import mouse
import pystray
from PIL import Image, ImageDraw
import win32gui
import win32con

start_moving = False
lock_overtime = 150
compose_key = 'alt+shift+ctrl+right'
hwnd = None

# 显示窗口
def show_console():
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 1)

# 隐藏任务栏图标
def hide_console():
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 0)

# 显示窗口操作
def on_show(icon, item):
    show_console()

# 退出窗口和程序
def on_exit(icon, item):
    global exit_program
    exit_program = True
    icon.stop()
    os._exit(0)

# 启动托盘
def run_icon():
    icon.run()

# 鼠标点击监听
def on_click(x, y, button, pressed):
    global start_moving
    if pressed:  # 如果鼠标有按压则停止自动移动
        start_moving = False

# 鼠标滚动监听
def on_scroll(x, y, dx, dy):
    global start_moving
    start_moving = False  # 如果鼠标有滚动, 则停止自动移动

# 热键切换程序启闭
def toggle_activation_state(e=None):
    global is_active
    is_active = not is_active

# 检查窗口状态
import win32api

# 检查窗口状态
import ctypes

# 检查窗口状态
def check_window_status():
    global hwnd
    # 获取当前控制台窗口句柄
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    while True:
        time.sleep(0.5)
        if hwnd is not None:
            foreground_window = win32gui.GetForegroundWindow()
            if foreground_window != hwnd:
                # 隐藏任务栏图标
                hide_console()

def move_mouse():
    global start_moving, is_active, exit_program
    last_x, last_y = pyautogui.position()
    last_time = time.time()
    is_active = True
    start_moving = False

    while True:
        if exit_program:
            return
        if is_active:
            x, y = pyautogui.position()
            current_time = time.time()
            if last_x == x and last_y == y:
                elapsed_time = current_time - last_time
                if elapsed_time >= lock_overtime:
                    start_moving = True
                while start_moving and is_active:
                    autoit.mouse_move(100, 100, speed=10)
                    time.sleep(0.1)
                    x, y = pyautogui.position()
                    if x != 100 or y != 100:
                        start_moving = False
                    autoit.mouse_move(200, 200, speed=10)
                    time.sleep(0.1)
                    x, y = pyautogui.position()
                    if x != 200 or y != 200:
                        start_moving = False
                    last_x, last_y = x, y
                    last_time = time.time()
            else:
                last_x, last_y = x, y
                last_time = time.time()
                start_moving = False
            time.sleep(5)
        else:
            time.sleep(5)

if __name__ == '__main__':
    try:
        hide_console()
        exit_program = False

        icon = pystray.Icon("lockscreen", Image.open("lock.png"))
        icon.menu = pystray.Menu(pystray.MenuItem('显示', on_show), pystray.MenuItem('退出', on_exit))

        tray_thread = threading.Thread(target=run_icon)
        tray_thread.start()

        print('防自动锁屏程序开启!')

        mouse_thread = threading.Thread(target=move_mouse)  # 鼠标自动移动线程
        mouse_listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)  # 监听鼠标滚动线程
        keyboard.add_hotkey(compose_key, toggle_activation_state)  # 停止热键监听
        check_window_thread = threading.Thread(target=check_window_status)  # 检查窗口状态线程

        mouse_thread.start()
        mouse_listener.start()
        check_window_thread.start()
        mouse_thread.join()
        mouse_listener.join()
        check_window_thread.join()

    except Exception as e:
        print(e)
        input("按任意键")
        os._exit(0)
