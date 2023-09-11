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

