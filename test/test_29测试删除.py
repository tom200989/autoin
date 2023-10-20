import os
import shutil
import subprocess
import sys
import psutil

local_path = r'D:/autocase/patch/p_huayan_20231020100105.zip'

def kill_exe(_exe):
    """
    关闭指定进程
    java.exe: sonar.bat进程
    pgAdmin4.exe: 数据库进程
    """
    print(f'正在关闭{_exe}....')
    for proc in psutil.process_iter(['pid', 'name']):
        # 检查进程名
        if proc.info['name'] == _exe:
            print(f'找到进程{_exe},正在关闭...')
            # 杀掉进程
            try:
                proc.kill()
            except Exception as error:
                if 'NoSuchProcess' in str(error): print('该进程已关闭')

    print(f'{_exe}已全部关闭!')

def is_exe_mode():
    """
    判断当前是否是exe模式
    :return: True: exe模式
    """
    return getattr(sys, 'frozen', False)

def filter_info(text):
    """
    查询文件是否被占用
    :return: 0: 未被占用, 1: 被占用, -1: 查询失败
    """
    exes_pids = {}
    # 检测是否有 "No matching handles found" -- 出现该字符表示文件未被占用
    if "No matching handles found" in text:
        return 0, exes_pids, '文件未被占用'

    # 过滤出含有exe的全部行
    lines = [line for line in text.splitlines() if ".exe" in line]
    # 提取出字符串`pid`前的字符(如:winrdlv3.exe) 以及提取出字符串`pid`和`type`之间的字符(如:9408   type: 9408)

    for line in lines:
        # 提取出字符串`pid`前的字符(如:winrdlv3.exe)
        exe_name = line.split('pid')[0].strip()
        # 提取出字符串`pid`和`type`之间的字符(如:9408   type: 9408)
        pid = line[line.find('pid:') + len('pid:'):line.find('type')].strip()
        # 填入字典
        exes_pids[exe_name] = pid

    if len(exes_pids) > 0:
        return 1, exes_pids, '文件被占用'
    else:
        return 0, exes_pids, '文件未被占用'

def find_who_occupt(file_path):
    """
    查询文件是否被占用
    :return: 0: 未被占用, 1: 被占用, -1: 查询失败
    """
    # 切换到handle.exe所在目录
    if is_exe_mode():
        os.chdir(os.path.dirname(sys.executable))  # 切换到exe所在目录
        handle_exe = os.path.join(os.getcwd(), 'handle')  # handle.exe所在目录
        os.chdir(handle_exe)  # 切换到handle.exe所在目录
    else:
        os.chdir(r'D:\project\python\autoin\autoin\demo\handle')  # 切换到handle.exe所在目录
    # 启动进程占用查询
    process = subprocess.Popen(f'handle64.exe {file_path}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if stdout:
        oc_state, oc_exes, oc_tip = filter_info(stdout.decode('gbk'))
        return oc_state, oc_exes, oc_tip  # 0,1
    if stderr:
        return -1, {}, f'查询失败: {stderr.decode("gbk")}'

# print(find_who_occupt(local_path)) # 查看文件被谁占用
