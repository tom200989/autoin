import autoit
import time
import threading
import keyboard

stop_program = False

def move_mouse():
    while True:
        if not stop_program:
            autoit.mouse_move(100, 100, speed=10)
            time.sleep(1)
            autoit.mouse_move(200, 200, speed=10)
            time.sleep(1)

def listen_for_exit_key():
    global stop_program
    stop_program = not stop_program



# 创建一个新线程用于移动鼠标
mouse_thread = threading.Thread(target=move_mouse)

# 使用add_hotkey来监听Ctrl+P组合键
keyboard.add_hotkey('alt+shift+ctrl+right', listen_for_exit_key)

mouse_thread.start()
mouse_thread.join()
