import subprocess

from b00_checknet import *
from cminio_tools import *
from ctmp_tools import *

def check_box_version():
    """
    查询母盒最新版本
    :return: True 有新版本, False 无新版本
    """
    # 检查是否minio连接
    minio_state, minio_tip, minio_client = check_minio_connect()
    if not minio_state:
        tmp_print(f"x minio连接失败{minio_tip}")
        return False
    tmp_print(f"√ minio连接成功:{minio_tip}")

    # 获取minio的box版本号
    lastest_mversion = get_motherbox_version(minio_motherbox_root)
    if lastest_mversion is None:
        tmp_print(f"x 获取minio的box版本号失败")
        return False

    # 判断版本大小
    if current_mversion < lastest_mversion:
        tmp_print(f"当前版本: {current_mversion}, 最新版本: {lastest_mversion}")
        return True
    else:
        tmp_print(f"当前版本: {current_mversion}, 无最新版本")
        return False

def update_box():
    # # 检查网络是否畅通
    # is_network = check_all_nets(is_adb=False)
    # if is_network:
    #     # 如果有新版本, 则更新
    #     need_update = check_box_version()
    #     if need_update:
    #         # 下载母盒辅助器
    #         # todo 2023/9/11
    #         # 启动母盒辅助器 (D:\project\python\autoin\case\motherbox\build\exe.win-amd64-3.11\mbh\a00_boxhelper.exe)
    #         boxhelp_path = os.path.join(motherbox_exedir, 'mbh', 'a00_boxhelper.exe')
    #         boxhelp_exe = subprocess.Popen([boxhelp_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
    #         tmp_print("启动母盒辅助器进程ID:", boxhelp_exe.pid)
    #     else:
    #         tmp_print("当前没有最新母盒版本, 无需更新")
    #     return need_update
    #
    # else:
    #     tmp_print("网络异常, 请根据以上提示检查网络相关连接!")
    #     return False
    pass
