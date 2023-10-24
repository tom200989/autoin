# -*- coding: utf-8 -*-

import sys
from queue import Empty, Queue
from threading import Thread
import inspect
import time
import os

_BAR_SIZE = 20  # 进度条长度
_KILOBYTE = 1024  # 缓冲区大小 1KB
_FINISHED_BAR = '#'  # 进度条完成的标志
_REMAINING_BAR = '-'  # 进度条未完成的标志

_UNKNOWN_SIZE = '?'  # 未知文件大小
_STR_MEGABYTE = ' MB'  # MB

_HOURS_OF_ELAPSED = '%d:%02d:%02d'  # 时分秒
_MINUTES_OF_ELAPSED = '%02d:%02d'  # 分秒

_RATE_FORMAT = '%5.2f'  # 百分比
_PERCENTAGE_FORMAT = '%3d%%'  # 百分比
_HUMANINZED_FORMAT = '%0.2f'  # MB

# _DISPLAY_FORMAT = '|%s| %s/%s %s [elapsed: %s left: %s, %s MB/sec]' # toat 修改点1: 去掉bar
_DISPLAY_FORMAT = '%s/%s %s [已用时: %s 预估剩余: %s, %s MB/sec]'  # 自定义显示格式

_REFRESH_CHAR = '\r'

class Progress(Thread):

    def __init__(self, interval=1, stdout=sys.stdout):
        Thread.__init__(self)
        self.prefix = ''
        self.daemon = True
        self.total_length = 0
        self.interval = interval
        self.object_name = None

        self.last_printed_len = 0
        self.current_size = 0
        self.stdout = stdout

        self.display_queue = Queue()
        self.initial_time = time.time()
        self.start()

    def set_meta(self, total_length, object_name):
        """
        设置文件大小和文件名
        :param total_length:  文件大小
        :param object_name:  文件名
        """
        self.total_length = total_length
        self.object_name = object_name
        # self.prefix = self.object_name + ': ' if self.object_name else '' # toat 修改点2: 把object_name该为当前进度
        self.prefix = '当前进度: ' if self.object_name else ''

    def run(self):
        """
        强制实现
        """
        displayed_time = 0
        while True:
            try:
                # display every interval secs
                task = self.display_queue.get(timeout=self.interval)
            except Empty:
                elapsed_time = time.time() - self.initial_time
                if elapsed_time > displayed_time:
                    displayed_time = elapsed_time
                self.print_status(current_size=self.current_size, total_length=self.total_length, displayed_time=displayed_time, prefix=self.prefix)
                continue

            current_size, total_length = task
            displayed_time = time.time() - self.initial_time
            self.print_status(current_size=current_size, total_length=total_length, displayed_time=displayed_time, prefix=self.prefix)
            self.display_queue.task_done()
            if current_size == total_length:
                # once we have done uploading everything return
                self.done_progress()
                return

    def update(self, size):
        """
        更新进度
        :param size: 需更新的当前进度
        """
        if not isinstance(size, int):
            raise ValueError('{} type can not be displayed. '
                             'Please change it to Int.'.format(type(size)))

        self.current_size += size
        self.display_queue.put((self.current_size, self.total_length))

    def done_progress(self):
        """
        完成进度
        """
        self.total_length = 0
        self.object_name = None
        self.last_printed_len = 0
        self.current_size = 0

    def print_status(self, current_size, total_length, displayed_time, prefix):
        """
        控制台打印进度
        :param current_size: 当前上传大小
        :param total_length:  文件总大小
        :param displayed_time:  已用时
        :param prefix:  打印前缀
        """
        formatted_str = prefix + format_string(current_size, total_length, displayed_time)
        # 如果  formatted_str 的字符中不包含 5% 10% ... 等5的倍数的百分比, 则不打印
        if not any([f'{i}%' in formatted_str for i in range(5, 100, 5)]):
            return
        # self.stdout.write(_REFRESH_CHAR + formatted_str + ' ' * max(self.last_printed_len - len(formatted_str), 0)) # toat: 修改点3: 替换系统打印
        # self.stdout.flush() # toat: 修改点3: 替换系统打印(替换成下方的tmp_print)

        progress_content = formatted_str + ' ' * max(self.last_printed_len - len(formatted_str), 0)
        if '100%' in progress_content:
            tmp_print('<enter>', progress_content)
        else:
            tmp_print('<tmpg>', progress_content)

        self.last_printed_len = len(formatted_str)

def seconds_to_time(seconds):
    """
    计算已用时
    :param seconds:
    """
    minutes, seconds = divmod(int(seconds), 60)
    hours, m = divmod(minutes, 60)
    if hours:
        return _HOURS_OF_ELAPSED % (hours, m, seconds)
    else:
        return _MINUTES_OF_ELAPSED % (m, seconds)

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
        time.sleep(0.001)  # 加阻塞延迟的目的是为了让控制台不要刷新那么快以至于什么都看不到
    elif types == 2:  # 强制换行 <enter>
        print(f"\n{pre_align}\t--> {times} ===> {content}")
    else:
        print(f"{pre_align}\t--> {times} ===> {content}")

def format_string(current_size, total_length, elapsed_time):
    """
    格式化打印内容
    :param current_size:  当前上传大小
    :param total_length:  文件总大小
    :param elapsed_time:  已用时
    """
    n_to_mb = current_size / _KILOBYTE / _KILOBYTE
    elapsed_str = seconds_to_time(elapsed_time)

    rate = _RATE_FORMAT % (n_to_mb / elapsed_time) if elapsed_time else _UNKNOWN_SIZE
    frac = float(current_size) / total_length
    # bar_length = int(frac * _BAR_SIZE) # toat 修改点1: 去掉bar
    # bar = (_FINISHED_BAR * bar_length + _REMAINING_BAR * (_BAR_SIZE - bar_length)) # toat 修改点1: 去掉bar
    percentage = _PERCENTAGE_FORMAT % (frac * 100)
    left_str = (seconds_to_time(elapsed_time / current_size * (total_length - current_size)) if current_size else _UNKNOWN_SIZE)

    humanized_total = _HUMANINZED_FORMAT % (total_length / _KILOBYTE / _KILOBYTE) + _STR_MEGABYTE
    humanized_n = _HUMANINZED_FORMAT % n_to_mb + _STR_MEGABYTE

    # return _DISPLAY_FORMAT % (bar, humanized_n, humanized_total, percentage, elapsed_str, left_str, rate) # toat 修改点1: 去掉bar
    return _DISPLAY_FORMAT % (humanized_n, humanized_total, percentage, elapsed_str, left_str, rate)
