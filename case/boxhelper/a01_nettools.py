import subprocess
import requests
import re
from a02_miniotools import *
from zboxtools import *

# ---------------------------------------------- wifi强度状态 ----------------------------------------------
def check_pc_wifi(target_wifi="EF-office"):
    """
    wifi强度状态
    :return: 状态+错误信息
    """
    try:
        cmd_output = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], universal_newlines=True, encoding='gbk')
        wifi_info = re.findall(r"SSID\s+:\s+(.*?)\n", cmd_output)
        if target_wifi in wifi_info:
            tmp_print(f"√ 本机已连接 {target_wifi} WiFi")
            return True
        else:
            tmp_print(f"x 本机未连接 {target_wifi} WiFi,请将本机连接到 {target_wifi}")
            return False
    except Exception as e:
        tmp_print(f"x 检查本机WiFi时出错: {e}")
        return False

# ---------------------------------------------- 外网状态 ----------------------------------------------
def check_google():
    urls = ["https://www.google.com"]
    for url in urls:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                tmp_print(f"√ 本机连接外网正常")
                return True
            else:
                tmp_print(f"x {url} 本机连接异常({response.status_code})")
                return False
        except Exception as e:
            tmp_print(f"x {url} 本机连接失败: {e}")
            return False

# ---------------------------------------------- minio存储桶状态 ----------------------------------------------
def check_minio():
    # 检查minio连接
    minio_state, minio_tip, _ = check_minio_connect()
    if minio_state:
        tmp_print(f"√ minio连接成功:{minio_tip}")
    else:
        tmp_print(f"x minio连接出错: {minio_tip}")

    return minio_state

# ---------------------------------------------- 手机wifi状态 ----------------------------------------------

# ---------------------------------------------- 检查全部环境 ----------------------------------------------
def check_pingnet():
    """
    检查全部环境(不检查adb)
    """
    target_wifi = "EF-office"
    state_map = {  #
        'state_pc_wifi': [check_pc_wifi(target_wifi), f'tips: 请把本机连接到{target_wifi}!(可能会导致无法运行脚本)'],  # 本机wifi连接
        'state_google': [check_google(), 'tips: 当前访问外网异常!(可能会导致APP无法配网)'],  # 外网连接检测
        'state_minio': [check_minio(), 'tips: 当前访问minio存储桶异常!(可能会导致无法查看压测数据)'],  # minio存储桶
    }

    tmp_print('')
    tmp_print('>' * 50)
    tmp_print('网络环境检测结果如下: ')
    final_state = True
    for state_key, state_value in state_map.items():
        if not state_value[0]:
            final_state = False
            tmp_print(state_value[1])

    if final_state:
        tmp_print('√ 测试网络环境通过!')
    else:
        tmp_print('x 测试网络环境异常!')
    tmp_print('>' * 50)

    return final_state

pass
