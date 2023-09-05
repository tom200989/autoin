import datetime
import inspect
import os
import socket
import sys
import time

root_dir = 'D:/autocase'  # 根目录
patch_dir = root_dir + '/case_log'  # 运行日志目录

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

# 使用ord()函数判断
def custom_len(s):
    length = 0
    for char in s:
        if ord(char) < 128:
            length += 1
        else:
            length += 2
    return length

# 拼接标题
def mer_title(content):
    """
    拼接标题
    :param content: 标题内容
    :return: 拼接后的标题
    """
    total_len = 60
    content_len = custom_len(content)
    left_len = (total_len - content_len) // 2
    right_len = total_len - content_len - left_len
    return f"{'-' * left_len}{content}{'-' * right_len}"

# 临时控制台打印 (不写入文件)
def tmp_print(*args):
    """
    工具: 临时控制台打印 (不写入文件)
    :param args: 打印内容
    """

    # types: 1 --> 表示 打印进度
    # types: 2 --> 表示 普通打印加入换行符
    types = 0
    # 对于输入参数的第一个特殊处理
    if args and args[0] == '<tmpg>':
        types = 1
        args = args[1:]
    elif args and args[0] == '<enter>':
        types = 2
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

# 获取电脑名称(如huilinxu01-nb.efsz.com)
def get_computer_name():
    try:
        computer_name = socket.getfqdn()
        return computer_name
    except Exception as e:
        tmp_print('获取设备全名出错: ', e)
        return None

# 获取电脑环境变量
def get_computer_env():
    env_str = str(os.getenv('path'))
    envs = list(env_str.split(';'))
    print(envs)

