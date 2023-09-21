import psutil
import time

import subprocess

# 检查chrome的版本

def is_process_running(process_name):
    try:
        # 遍历所有运行中的进程
        for proc in psutil.process_iter():
            # 获取进程详情作为字典
            process_info = proc.as_dict(attrs=['pid', 'name', 'create_time'])
            # 检查进程名是否与目标进程名相匹配
            if process_name.lower() in process_info['name'].lower():
                return True
        return False
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        print('安装失败, 程序被终止')
        return False

# 指定ChromeSetup.exe的路径
chrome_setup_path = r"C:\Users\huilin.xu\Downloads\ChromeSetup.exe"
subprocess.Popen(chrome_setup_path)

# 等待ChromeSetup.exe进程结束
while is_process_running('ChromeSetup.exe'):
    time.sleep(1)

print("Chrome 安装完成")
