from __future__ import print_function
import os
import sys
import ctypes
from tkinter import messagebox

import chardet
if sys.version_info[0] == 3:
    import winreg as winreg
else:
    import _winreg as winreg

import ctypes
import datetime
import inspect
import os
import platform
import socket
import stat
import sys
import time
import winreg
import psutil
import winapps
import requests
import re
import shutil
import subprocess
from prompt_toolkit import PromptSession
from prompt_toolkit.shortcuts import checkboxlist_dialog
from prompt_toolkit.shortcuts import radiolist_dialog
from concurrent.futures import ProcessPoolExecutor, TimeoutError
from functools import partial

CMD = r"C:\Windows\System32\cmd.exe"
FOD_HELPER = r'C:\Windows\System32\fodhelper.exe'
PYTHON_CMD = "python"
REG_PATH = 'Software\Classes\ms-settings\shell\open\command'
DELEGATE_EXEC_REG_KEY = 'DelegateExecute'

test_mode = False  # 是否为测试模式(默认为测试模式, 不重启)

motherbox_version = 1000  # 当前母盒版本号
root_dir = 'D:/autocase'  # 本地根目录
case_log_dir = root_dir + '/case_log'  # 运行日志目录
boxhelper_dir = root_dir + '/boxhelper'  # 母盒辅助器目录
chromesetup_dir = root_dir + '/chromesetup'  # ChromeSetup.zip目录
sdk_dir = root_dir + '/sdk'  # sdk目录
jdk_dir = root_dir + '/jdk'  # jdk目录
gradle_dir = root_dir + '/gradle'  # gradle目录
nodejs_dir = root_dir + '/nodejs'  # nodejs目录
driver_dir = root_dir + '/driver'  # driver目录
sys_env_dir = root_dir + '/sys_env'  # 系统环境变量缓存目录
sys_env_txt = sys_env_dir + '/sys_env.txt'  # 系统环境变量缓存文件
patch_root = root_dir + '/patch'  # patch目录(脚本目录)
patch_cdir_prefix = 'p_'  # patch目录下的子目录前缀
boxhelper_exe_p = 'a00_boxhelper.exe'  # 母盒辅助器的exe文件名
uninst_dirs = [chromesetup_dir, sdk_dir, jdk_dir, gradle_dir, nodejs_dir, driver_dir, sys_env_dir]  # 一键删除时需清空的目录
adb_exe = os.path.join(sdk_dir, 'platform-tools', 'adb.exe')  # adb.exe文件名

# ndk的版本(固定)
ndk_target = '25.1.8937393'

# node.js的版本(固定)
node_target = '16.18.1'
minio_nodejs = 'autocase/android/env/nodejs/nodejs.zip'  # nodejs.zip的路径

# appium的版本(固定)
appium_target = '1.22.3'

# minio配置信息
endpoint = 'minio.ecoflow.com:9000'
access_key = 'EQS4J84JGJCDYNENIMT1'
secret_key = '8Vgk11c9bDOpZPTJMexPLrxZpzEOqro+jZyAUh+a'
bucket_name = 'rnd-app-and-device-logs'
minio_config = 'minio_config.json'

# 母盒minio路径
minio_motherbox_root = 'autocase/android/motherbox/'  # motherbox的根目录 (注意, 要加一个`/`结尾,可能会有重复的前缀目录, 也会被搜索出来)
# 母盒辅助器路径
minio_boxhelper_root = 'autocase/android/boxhelper/'  # boxhelper的根目录 (注意, 要加一个`/`结尾,可能会有重复的前缀目录, 也会被搜索出来)

# ChromeSetup.zip路径
minio_chrome_zip = 'autocase/android/env/chromes/chrome/ChromeSetup.zip'  # chrome.exe的路径
# chromedriver目录路径
minio_chromedriver_root = 'autocase/android/env/chromes/chromedriver/'  # chromedriver目录路径(需遍历)

# sdk.zip路径
# todo 2023/10/9 正式环境下修改回 sdk.zip
minio_sdk = 'autocase/android/env/sdk/sdk.zip'  # sdk.zip的路径
# jdk.zip路径
minio_jdk = 'autocase/android/env/jdk/jdk.zip'  # jdk.zip的路径
# gradle.zip路径
minio_gradle = 'autocase/android/env/gradle/gradle.zip'  # gradle.zip的路径

# patch的角色目录路径
minio_patch_root = 'autocase/android/patch/'  # patch的根目录 (注意, 要加一个`/`结尾,可能会有重复的前缀目录, 也会被搜索出来)

# driver.zip路径
minio_driver_root = 'autocase/android/env/driver/'  # driver的根路径
target_driver = {  # 当前自动化脚本所需要的驱动
    'ch341ser.inf': '该驱动用于读取芯片日志',  #
    'ch343ser.inf': '该驱动用于读取芯片日志',  #
    'slabvcp.inf': '该驱动用于控制继电器',  #
}  #

# 环境变量注册表
env_reg = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
default_chrome = r'C:\Program Files\Google\Chrome\Application'  # 默认chrome安装目录

def get_env_path():
    """
    获取环境变量(此做法能不区分path大小写)
    """
    # 获取所有环境变量
    all_env_vars = os.environ
    # 将所有键转换为小写，并存储在一个字典中
    lowercase_env_vars = {k.lower(): v for k, v in all_env_vars.items()}
    # 获取"path"环境变量（不区分大小写）
    path_value = lowercase_env_vars.get('path', None)
    if path_value:
        return path_value
    else:
        return None

def is_dir_exits_above_100mb(folder_path):
    """
    判断文件夹是否存在, 并且文件夹大小是否大于100MB
    :param folder_path:
    :return:  True: 存在且大于1MB, False: 不存在或小于100MB
    """
    if not os.path.isdir(folder_path):
        return False

    folder_size = sum(os.path.getsize(os.path.join(root, file)) for root, _, files in os.walk(folder_path) for file in files)
    return folder_size >= 100 * 1024 * 1024

def kill_exe(_exe):
    """
    关闭指定进程
    java.exe: sonar.bat进程
    pgAdmin4.exe: 数据库进程
    """
    tmp_print(f'正在关闭{_exe}....')
    for proc in psutil.process_iter(['pid', 'name']):
        # 检查进程名
        if proc.info['name'] == _exe:
            tmp_print(f'找到进程{_exe},正在关闭...')
            # 杀掉进程
            try:
                proc.kill()
            except Exception as error:
                if 'NoSuchProcess' in str(error): tmp_print('该进程已关闭')

    tmp_print(f'{_exe}已全部关闭!')

def del_rw(action, name, exc):
    """
    切换文件夹权限(管理员)
    :param action:
    :param name:
    :param exc:
    """
    # 修改权限
    os.chmod(name, stat.S_IWRITE)
    try:
        # 删除文件夹
        os.remove(name)
    except Exception as error:
        # traceback.print_exc()
        tmp_print('文件夹被进程占用, os.remove失败, 即将强制删除: ', error)
        os.popen(f'rd /s /q {name}')  # 如果当前文件夹被占用, 则强制删除

def get_today():
    """
    获取今天日期
    :return: 今天日期
    """
    today = time.strftime("%Y%m%d", time.localtime())
    return today

# 写入脚本日志内容 (2022-12-03 18:00:00 ===> xxxx)
def out(content):
    """
    输出的脚本日志内容 (2022-12-03 18:00:00 ===> xxxx)
    :param content: 内容
    """
    # 创建目录
    if not os.path.exists(case_log_dir):
        os.makedirs(case_log_dir)
    # 创建文件
    patch_path = case_log_dir + f'/{get_today()}_patch_log.txt'
    if not os.path.exists(patch_path):
        open(patch_path, 'w').close()
    # 2022-11-29 17:25:25 ==> xxxxxx
    # a和a+的区别是a+可以同时读取文件内容, a只能写入.如果想在追加同时读取文件, 则需要调用file.seek(0)方法把文件指针移到开头
    with open(patch_path, 'a') as file:
        date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        final = date_time + " ===> " + content
        file.write(final + "\n")
        file.flush()

# 临时控制台打印 (不写入文件)
def tmp_print(*args):
    """
    工具: 临时控制台打印 (不写入文件)
    :param args: 打印内容
    """

    # types: 1 --> 表示 打印进度
    # types: 2 --> 表示 普通打印加入换行符
    # types: 3 --> 表示 不打印单记录在本地
    types = 0
    # 对于输入参数的第一个特殊处理
    if args and args[0] == '<tmpg>':
        types = 1
        args = args[1:]
    elif args and args[0] == '<enter>':
        types = 2
        args = args[1:]
    elif args and args[0] == '<noprint>':
        types = 3
        args = args[1:]

    # 对于剩余的参数或所有的参数
    content = "".join(map(str, args))

    # 获取函数名
    caller_frame = inspect.stack()[1]
    method_name = caller_frame.function
    # 获取文件名
    file_name = os.path.basename(caller_frame.filename)
    # 打印出来
    pre_tag = f"[{file_name}: {method_name}()]"
    # width = ((len(pre_tag) - 1) // 10 + 1) * 10 # 动态计算
    width = 40
    times = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    pre_align = "{:<{width}}".format(pre_tag, width=width)
    if types == 1:  # 打印进度 <tmpg>
        print(f"\r{pre_align}\t--> {times} ===> {content}", end='')
        time.sleep(0.001)  # 加阻塞延迟的目的是为了让控制台不要刷新那么快以至于什么都看不到
    elif types == 2:  # 强制换行 <enter>
        print(f"\n{pre_align}\t--> {times} ===> {content}")
        out(content)
    elif types == 3:  # 不打印但记录在本地
        out(content)
    else:  # 普通打印
        print(f"{pre_align}\t--> {times} ===> {content}")
        out(content)

def get_nowexe_dir():
    """
    获取当前文件执行的目录 (注意,如果有多级目录的话, 该端代码要写在真正获取目录的地方)
    :return:  当前文件执行的目录
    """
    if getattr(sys, 'frozen', False):
        src_dir = os.path.dirname(sys.executable)
    else:  # 源文件的路径
        src_dir = os.path.dirname(os.path.abspath(__file__))  # 当前工程目录
    return src_dir

def choice_pancel(title, text, items, fun_cancel):
    """
    选择面板选项
    """
    # selects = checkboxlist_dialog(title=title, text=text, values=items).run()
    selects = radiolist_dialog(title=title, text=text, values=items).run()
    if not selects:  # 如果没有选择任何选项
        if fun_cancel:  # 且回调函数不为空
            fun_cancel()  # 执行回调函数(带参)

        else:  # 回调函数为空(外部也不告知如何处理)
            tmp_print("x 未选择任何选项")  # 则默认打印
        return None
    return selects[0]

def back_func(func, argk=None):
    """
    执行回退的函数 (返回的是一个新的函数对象，这个对象内部已经“记住了”原函数和预设的参数)
    这个做法可以避免传递函数时后边携带一大堆参数
    :param func: 点击cancel时回退的函数
    :param argk: 函数所需的参数
    :return:
    """
    if argk is None:
        return func
    else:
        return partial(func, func_cancel=argk)

def get_pack_dirname():
    """
    获取打包后的目录名(exe.win-amd64-3.11)
    """
    platform_name = platform.system().lower()
    if 'win' in platform_name: platform_name = 'win'
    architecture = platform.machine().lower()
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    directory_name = f"exe.{platform_name}-{architecture}-{python_version}"
    return directory_name

def is_process_running(process_name):
    """
    检查进程是否运行
    :param process_name: 进程名
    :return: True 运行中, False 未运行
    """
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
        tmp_print(f'获取当前进程{process_name}出错')
        return False

def check_exe(target_exe):
    """
    获取指定exe的安装信息
    :return: [文件名, 安装路径, 版本, 卸载命令]
    """
    exe = [app.name for app in winapps.search_installed(target_exe)]
    if exe and len(exe) > 0:
        target_exe = target_exe.lower()
        for ex in winapps.list_installed():
            exe_name = str(ex.name).lower()
            if exe_name in target_exe or target_exe in exe_name:
                # 文件名, 安装路径, 版本, 卸载命令
                exe_name = ex.name
                exe_install_path = str(ex.install_location)
                if exe_install_path == '' or exe_install_path is None: exe_install_path = str(ex.install_source)
                exe_version = ex.version
                exe_uninstall_string = ex.uninstall_string
                return_info = [exe_name, exe_install_path, exe_version, exe_uninstall_string]
                return return_info

    return None

def get_exe_install_path(target_exe):
    """
    获取exe安装路径
    :return: exe安装路径
    """
    try:
        # 获取chrome安装路径
        exe = [app.name for app in winapps.search_installed(target_exe)]
        if exe and len(exe) > 0:
            target_exe = target_exe.lower()
            for ex in winapps.list_installed():
                exe_name = str(ex.name).lower()
                if exe_name in target_exe or target_exe in exe_name:
                    exe_install_path = str(ex.install_location)
                    if exe_install_path == '' or exe_install_path is None:
                        exe_install_path = str(ex.install_source)
                    return exe_install_path
        return None
    except Exception as e:
        tmp_print(f'获取{target_exe}安装路径失败, {e}')
        return None

def need_env_paths(chrome_install_path=default_chrome):
    """
    需要配置的环境变量路径
    :param chrome_install_path: chrome安装路径(动态变化)
    :return:  需要配置的环境变量路径列表
    """
    if chrome_install_path is None: chrome_install_path = default_chrome
    # SDK路径
    test_sdk_home = sdk_dir
    test_sdk_buildtools_path = os.path.join(test_sdk_home, 'build-tools')
    test_ndk_path = os.path.join(test_sdk_home, 'ndk')
    test_ndk_25_path = os.path.join(test_ndk_path, ndk_target)
    test_platforms_path = os.path.join(test_sdk_home, 'platforms')
    test_platform_tools_path = os.path.join(test_sdk_home, 'platform-tools')
    test_tools_bin_path = os.path.join(test_sdk_home, 'tools', 'bin')

    # JDK路径
    test_jdk_home = jdk_dir
    test_jdk_bin_path = os.path.join(test_jdk_home, 'bin')

    # chrome-application路径
    test_chrome_home = chrome_install_path  # 这个是动态变化

    # gradle/bin路径
    test_gradle_home = gradle_dir
    test_gradle_bin_path = os.path.join(test_gradle_home, 'bin')

    # 测试路径列表
    test_paths = [  # sdk
        test_sdk_home,  # /sdk
        test_sdk_buildtools_path,  # /sdk/build-tools
        test_ndk_path,  # /ndk
        test_ndk_25_path,  # /ndk/25.1.8937393
        test_platforms_path,  # /platforms
        test_platform_tools_path,  # /platform-tools
        test_tools_bin_path,  # /tools/bin
        # jdk
        test_jdk_home,  # /jdk
        test_jdk_bin_path,  # /jdk/bin
        # chrome
        test_chrome_home,  # /chrome
        # gradle
        test_gradle_home,  # /gradle
        test_gradle_bin_path,  # /gradle/bin
    ]
    # 替换斜杠
    corrected_paths = [path.replace("/", "\\").replace("\\\\", "\\") for path in test_paths]
    return corrected_paths

def get_cur_envs():
    """
    获取当前环境变量
    """
    try:
        # 打开注册表，获取环境变量
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, env_reg) as key:
            original_path = winreg.QueryValueEx(key, 'Path')[0]
        return original_path
    except Exception as e:
        tmp_print(f'获取当前环境变量失败, {e}')
        return None

def backup_envs():
    """
    备份当前环境变量
    """
    try:
        # 创建目录
        tmp_print('正在备份环境变量...')
        if not os.path.exists(os.path.dirname(sys_env_txt)):
            os.makedirs(os.path.dirname(sys_env_txt))
        # 打开注册表，获取环境变量
        tmp_print('正在获取环境变量...')
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, env_reg) as key:
            original_path = winreg.QueryValueEx(key, 'Path')[0]
        # 备份到文件
        tmp_print('正在备份环境变量到文件...')
        with open(sys_env_txt, 'w') as file:
            file.write(original_path)
        tmp_print(f'环境变量备份完成: {sys_env_txt}')
        return True
    except Exception as e:
        tmp_print(f'环境变量备份失败, {e}')
        return False

def add_need_envs():
    """
    在原有环境变量前添加新路径
    """
    try:
        tmp_print('正在添加环境变量...')
        # 需要配置的环境变量路径
        test_paths = need_env_paths(get_exe_install_path('chrome.exe'))
        tmp_print(f'正在配置所需的环境变量...')
        # 打开注册表，获取环境变量
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, env_reg, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            # 添加SDK根路径
            winreg.SetValueEx(key, 'ANDROID_HOME', 0, winreg.REG_EXPAND_SZ, sdk_dir)
            # 添加JDK根路径
            winreg.SetValueEx(key, 'JAVA_HOME', 0, winreg.REG_EXPAND_SZ, jdk_dir)

            original_path = winreg.QueryValueEx(key, 'Path')[0]
            # 把新路径添加到原始路径前面
            new_path = ';'.join(test_paths)+';%ANDROID_HOME%;%JAVA_HOME%' + ';' + original_path
            # # 更新环境变量
            winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(key)
        tmp_print('环境变量配置完成。')
        return True
    except Exception as e:
        tmp_print(f'环境变量配置失败, {e}')
        return False

def restore_envs():
    """
    从备份文件还原环境变量
    """
    try:
        if not os.path.exists(sys_env_txt):
            tmp_print('备份文件不存在，无法还原。')
            return
        tmp_print('正在还原环境变量...')
        # 从备份文件中读取环境变量
        with open(sys_env_txt, 'r') as file:
            original_path = file.read()
        tmp_print('正在还原环境变量到注册表...')
        # 打开注册表，设置环境变量
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, env_reg, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, original_path)
        tmp_print(f'环境变量已从 <{sys_env_txt}> 还原')
        tmp_print(get_cur_envs())

        if not test_mode:  # 非测试模式 - 重启
            input('环境变量还原完成, 请按任意键重启...')
            tmp_print('环境变量还原完毕, 5秒后重启电脑...(请勿操作)')
            time.sleep(3)
            os.system('shutdown -r -t 0')
        return True
    except Exception as e:
        tmp_print(f'环境变量还原失败, {e}')
        return False

def is_admin():
    """
    判断是否有管理员权限
    """
    try:
        tmp_print('正在判断是否有管理员权限...')
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        tmp_print(f'判断管理员权限失败, {e}')
        return False

def create_reg_key(key, value):
    """
    创建注册表键值对
    """
    try:
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, key, 0, winreg.REG_SZ, value)
        winreg.CloseKey(registry_key)
    except WindowsError:
        raise

def bypass_uac(cmd):
    """
    尝试绕过UAC
    """
    try:
        create_reg_key(DELEGATE_EXEC_REG_KEY, '')
        create_reg_key(None, cmd)
    except WindowsError:
        raise

# 检查端口是否被占用
def check_port(port=4725):
    """
    工具: 检测端口是否被引用
    :param port: 待检测端口
    :return: info = [False, "unknow", port, "unknow"]
        occupy: True为被占用
        result: 状态行信息
        port: 待检查端口
        pid: 进程PID
    """
    tmp_print(f"开始检查, 端口 = {str(port)}")
    # 检查端口占用状态
    result = subprocess.getoutput(f"netstat -ano | findstr {port}")
    result = result.split("\n")[0]
    # True 说明此时端口被占用
    occupy = len(result) > 0
    tmp_print(f"端口占用情况 {str(occupy)} (if True:被占用)")
    # 状态行有值 -- 截取PID
    pid = -1
    if occupy:
        if result.__contains__('TIME_WAIT'):  # 如果操作频繁, 端口未能反应, 则先等待
            tmp_print("操作频繁, 正在等待5秒...")
            time.sleep(3)  # 建议5秒
        if result.__contains__('LISTENING'):
            startIdx = str(result).index('LISTENING') + len('LISTENING')
            endIdx = len(str(result))
            pid = result[startIdx:endIdx].strip()
    info = [occupy, str(result), port, int(pid)]
    tmp_print(f"查询结果 {info}")
    return info

# 清理端口
def kill_port(port, pid):
    """
    工具: 手动清理端口
    :param port: 待清理端口
    :param pid: 待清理进程PID
    :return: True: 端口被销毁
    """

    # 如果外部没有传递PID -- 启动自动查询模式(根据端口查询)
    if pid == -1:
        tmp_print(f"未发现pid, 即将根据端口 {str(port)} 查询pid = -1")
        old_result = subprocess.getoutput(f"netstat -ano | findstr {str(port)}")
        # 如下可能存在:
        # TCP    0.0.0.0:4724           0.0.0.0:0              LISTENING       28220
        # TCP    0.0.0.0:4724           0.0.0.0:0              TIMEWAIT        0
        result = old_result.split("\n")[0]
        if len(result) > 0:
            if result.__contains__('TIME_WAIT'):  # 如果操作频繁, 端口未能反应, 则先等待
                tmp_print("操作频繁, 正在等待5秒...")
                time.sleep(3)  # 建议3秒
            if result.__contains__('LISTENING'):
                startIdx = str(result).index('LISTENING') + len('LISTENING')
                endIdx = len(str(result))
                pid = result[startIdx:endIdx].strip()
                tmp_print(f"查询到pid = {str(pid)}")

    # 清理指定PID进程
    tmp_print(f"开始清理, port = {str(port)}, pid = {str(pid)}")
    os.system(f'taskkill /f /pid {pid}')
    tmp_print(f"正在核对...")
    time.sleep(2)  # 建议2秒
    result = os.system(f'netstat -ano|findstr {str(port)}')
    is_success = len(str(result)) == 1
    if is_success:
        tmp_print("清理成功")
    else:
        tmp_print("清理失败")
    return is_success

def find_cdirs_prefix(target_dir, prefix):
    """
    查找指定目录下的所有子目录中符合前缀条件的子目录，并以字典形式返回
    :param target_dir: 指定目录
    :param prefix: 前缀
    :return: 符合前缀条件的子目录的字典（目录名作为key，路径作为value）
    """
    try:
        # 使用列表解析获取符合条件的目录
        cdirs = [os.path.abspath(os.path.join(target_dir, d)) for d in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, d)) and d.startswith(prefix)]
        # 使用字典推导式创建字典
        result_dict = {os.path.basename(dir_path): dir_path for dir_path in cdirs}
        # 按照目录名的ASCII码进行排序
        sorted_result_dict = dict(sorted(result_dict.items()))
        return sorted_result_dict if sorted_result_dict else None
    except Exception as e:
        tmp_print(f"查找脚本目录发生错误: {e}")
        return None

# 输入adb shell指令
def adb_shell(cmd, is_print_ori=False, adb_path=adb_exe):
    """
    输入adb shell指令
    :param cmd:  待执行的adb shell指令
    :param is_print_ori:  是否打印原始命令字符
    :param adb_path:  adb.exe文件路径
    :return:
    """
    inputCmd = str(cmd)
    executeDir = adb_path  # 写你的adb路径

    try:
        # 执行指令
        process = subprocess.Popen(inputCmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, cwd=executeDir)
        # 读取结果
        result = process.stdout.read().decode()
        # 删除ANSI转义字符
        new_result = remove_ansi(result)
        # 切割数据
        result_list = str(new_result).strip().split("\r\n")
        # 打印原始命令字符
        if is_print_ori:
            for re in result_list:
                tmp_print(re)
    except Exception as err:
        raise AssertionError('Execute adb command: {:s} error,{:s}'.format(inputCmd, err))

    return result_list

# 删除ANSI转义字符
def remove_ansi(result):
    ansi_escape_regex = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape_regex.sub('', result)

def where_cmd(find_cmd):
    """
    查找指定命令的路径
    :param find_cmd:  待查找的命令(如adb, appium)
    :return:  True: 存在, False: 不存在
    """
    # 执行CMD命令并获取输出
    result = subprocess.run(['where', find_cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # 判断命令是否成功执行
    if result.returncode == 0:
        path = result.stdout
        tmp_print(f'查找到: {path}')
        return True, path
    else:
        err = result.stderr
        tmp_print(f'未找到: {err}')
        return False, err

def restart_adb():
    try:
        subprocess.run(["adb", "kill-server"], universal_newlines=True, encoding='utf-8')
        subprocess.run(["adb", "start-server"], universal_newlines=True, encoding='utf-8')
        tmp_print("ADB服务已重启")
        return True
    except Exception as e:
        tmp_print(f"x 重启ADB服务时出错: {e}")
        return False

def check_adb_install():
    try:
        cmd_output = subprocess.check_output(["adb", "version"], universal_newlines=True, encoding='utf-8')
        if "Android Debug Bridge version" in cmd_output:
            tmp_print("√ ADB已安装")
            return True
        else:
            tmp_print("x ADB未安装")
            return False
    except Exception as e:
        tmp_print(f"x 检查ADB安装时出错: {e}")
        return False

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
    process = subprocess.Popen(f'handle64.exe /accepteula {file_path}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if stdout:
        oc_state, oc_exes, oc_tip = filter_info(stdout.decode('utf-8'))
        return oc_state, oc_exes, oc_tip  # 0,1
    if stderr:
        encoding_type = chardet.detect(stdout)['encoding']
        return -1, {}, f'查询失败: {stderr.decode(encoding_type)}'

def remove_who(file_path):
    """
    删除文件
    """
    try:
        count = 0
        if not os.path.exists(file_path): return True
        # 进入100秒的查询 -- 100秒如果依然被占用则直接抛出异常
        while count < 30:
            tmp_print('查询占用状态....')
            oc_state, oc_exes, oc_tip = find_who_occupt(file_path)
            if oc_state == 0:  # 如果未被占用
                tmp_print(f"文件已被释放: {file_path}")
                break
            elif oc_state == 1:  # 如果被占用
                tmp_print(f"文件被占用,正尝试杀死进程...")
                # 杀死占用进程
                for exe in oc_exes.keys():
                    # 杀死进程
                    tmp_print(f"./././ 正在杀死进程: {exe}:{oc_exes[exe]}")
                    kill_exe(exe)
                    os.system(f'taskkill /f /pid {oc_exes[exe]}')
                    time.sleep(1)
            else:
                tmp_print(f"查询异常,正在重试: {oc_tip}")
                continue
            # 休眠
            time.sleep(5)

        # 尝试删除文件
        os.remove(file_path)
        tmp_print(f"删除文件成功: {file_path}")
        return True
    except Exception as e:
        # 依然失败 - 直接抛出异常
        tmp_print(f"删除文件失败, 正在重试: {e}")
        raise Exception(f"删除文件失败: {file_path}")
