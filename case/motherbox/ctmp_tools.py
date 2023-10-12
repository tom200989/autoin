from __future__ import print_function
import os
import sys
import ctypes
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

test_mode = True  # 是否为测试模式(默认为测试模式, 不重启)

motherbox_version = 1000  # 当前母盒版本号
root_dir = 'D:/autocase'  # 本地根目录
patch_dir = root_dir + '/case_log'  # 运行日志目录
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
minio_sdk = 'autocase/android/env/sdk/sdk1.zip'  # sdk.zip的路径
# jdk.zip路径
minio_jdk = 'autocase/android/env/jdk/jdk.zip'  # jdk.zip的路径
# gradle.zip路径
minio_gradle = 'autocase/android/env/gradle/gradle.zip'  # gradle.zip的路径

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
    if not os.path.exists(patch_dir):
        os.makedirs(patch_dir)
    # 创建文件
    patch_path = patch_dir + f'/{get_today()}_scan_patch.txt'
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
        time.sleep(0.01)  # 加阻塞延迟的目的是为了让控制台不要刷新那么快以至于什么都看不到
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
        tmp_print('chrome安装失败, 程序被终止')
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
            original_path = winreg.QueryValueEx(key, 'Path')[0]
            # 把新路径添加到原始路径前面
            new_path = ';'.join(test_paths) + ';' + original_path
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
