from b00_checknet import *

def pull_wholog(lgt='xlog'):
    """
    导出日志
    :param lgt: 日志类型, 默认为xlog, 可选值为: xlog, macut
    """
    # 检查adb是否连接
    is_adb_conn = check_adb()
    if not is_adb_conn: return False
    # 导出xlog,macut日志到指定路径
    return adb_pull_wholog(lgt)
