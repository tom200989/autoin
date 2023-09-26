import datetime
import inspect
import os
import platform
import socket
import stat
import subprocess
import sys
import time

import psutil
import winapps
from prompt_toolkit import PromptSession
from prompt_toolkit.shortcuts import checkboxlist_dialog
from prompt_toolkit.shortcuts import radiolist_dialog
from concurrent.futures import ProcessPoolExecutor, TimeoutError

motherbox_version = 1000  # 当前母盒版本号
root_dir = 'D:/autocase'  # 本地根目录
patch_dir = root_dir + '/case_log'  # 运行日志目录
boxhelper_dir = root_dir + '/boxhelper'  # 母盒辅助器目录
chromesetup_dir = root_dir + '/chromesetup'  # ChromeSetup.zip目录
sdk_dir = root_dir + '/sdk'  # sdk目录
jdk_dir = root_dir + '/jdk'  # jdk目录
gradle_dir = root_dir + '/gradle'  # gradle目录
nodejs_dir = root_dir + '/nodejs'  # nodejs目录
boxhelper_exe_p = 'a00_boxhelper.exe'  # 母盒辅助器的exe文件名

# node.js的版本(固定)
node_target = '16.18.1'
minio_nodejs= 'autocase/android/env/nodejs/nodejs.zip'  # nodejs.zip的路径

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
minio_sdk = 'autocase/android/env/sdk/sdk1.zip'  # sdk.zip的路径
# jdk.zip路径
minio_jdk = 'autocase/android/env/jdk/jdk.zip'  # jdk.zip的路径
# gradle.zip路径
minio_gradle = 'autocase/android/env/gradle/gradle.zip'  # gradle.zip的路径

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
            fun_cancel()  # 执行回调函数
        else:  # 回调函数为空(外部也不告知如何处理)
            tmp_print("x 未选择任何选项")  # 则默认打印
        return None
    return selects[0]

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
                if exe_install_path == '' or exe_install_path is None:exe_install_path = str(ex.install_source)
                exe_version = ex.version
                exe_uninstall_string = ex.uninstall_string
                return_info = [exe_name, exe_install_path, exe_version, exe_uninstall_string]
                return return_info

    return []
