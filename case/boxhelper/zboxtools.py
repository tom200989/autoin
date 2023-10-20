import datetime
import inspect
import os
import shutil
import socket
import stat
import subprocess
import sys
import time

import psutil

boxhelper_version = 1  # 母盒辅助器版本号
root_dir = 'D:/autocase'  # 本地根目录
patch_dir = root_dir + '/case_log'  # 运行日志目录
motherbox_exe_p = 'a00_motherbox.exe'  # 母盒进程名

# minio配置信息
endpoint = 'minio.ecoflow.com:9000'
access_key = 'EQS4J84JGJCDYNENIMT1'
secret_key = '8Vgk11c9bDOpZPTJMexPLrxZpzEOqro+jZyAUh+a'
bucket_name = 'rnd-app-and-device-logs'
minio_config = 'minio_config.json'

minio_motherbox_root = 'autocase/android/motherbox/'  # motherbox的根目录

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
        time.sleep(2)
        # 删除文件夹
        os.remove(name)
    except Exception as error:
        # traceback.print_exc()
        tmp_print('文件夹被进程占用, os.remove失败, 即将强制删除: ', error)
        os.popen(f'rd /s /q {name}')  # 如果当前文件夹被占用, 则强制删除

def find_exe_path(exe_name):
    """
    根据进程名查找进程路径(绝对路径)
    :param exe_name:  进程名
    :return:  进程路径
    """
    for proc in psutil.process_iter(attrs=['pid', 'name', 'exe']):
        if proc.info['name'] and exe_name.lower() in proc.info['name'].lower():
            return proc.info['exe']

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
