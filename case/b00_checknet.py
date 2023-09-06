import subprocess
import requests
import re
from minio import Minio
from minio.error import S3Error
from ctmp_tools import *

# ---------------------------------------------- wifi强度状态 ----------------------------------------------
def check_pc_wifi(target_wifi="EF-office"):
    """
    wifi强度状态
    :return: 状态+错误信息
    """
    tmp_print(mer_title("正在检查本机WiFi状态..."))
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

# ---------------------------------------------- 后台环境状态 ----------------------------------------------
def check_ecoflow_server():
    tmp_print(mer_title("正在检查后台环境状态..."))
    urls = {  #
        "欧洲节点": "https://api-e.ecoflow.com/iot-service/health",  #
        "美国节点": "https://api-a.ecoflow.com/iot-service/health",  #
        "国内生产节点": "https://api-cn.ecoflow.com/iot-service/health",  #
        "海外UAT节点": "https://api-uat-aws.ecoflow.com/iot-service/health",  #
        "国内UAT节点": "https://api-uat2.ecoflow.com/iot-service/health"  #
    }

    states = []  # 状态列表
    for key, url in urls.items():
        try:
            response = requests.get(url)
            if response.status_code == 200:
                json_data = response.json()
                if json_data.get("status") == "UP":
                    tmp_print(f"√ {key} 连接正常.")
                    states.append(True)
                else:
                    tmp_print(f"x {key} 连接异常(服务器返回异常status!=`UP`).")
                    states.append(False)
            else:
                tmp_print(f"x {key} 连接异常({response.status_code}).")
                states.append(False)
        except Exception as e:
            tmp_print(f"x {key} 连接失败: {e}")
            states.append(False)

    # 查看全部状态
    for state in states:
        # 只要有一个状态为False, 就返回False
        if not state:
            return False
    # 全部状态为True, 返回True
    return True

# ---------------------------------------------- 外网状态 ----------------------------------------------
def check_google():
    tmp_print(mer_title("正在检查本机外网状态..."))
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

# ---------------------------------------------- adb连接状态 ----------------------------------------------
def __restart_adb__():
    tmp_print(mer_title("正在重启ADB服务..."))
    try:
        subprocess.run(["adb", "kill-server"], universal_newlines=True, encoding='utf-8')
        subprocess.run(["adb", "start-server"], universal_newlines=True, encoding='utf-8')
        tmp_print("ADB服务已重启")
        return True
    except Exception as e:
        tmp_print(f"x 重启ADB服务时出错: {e}")
        return False

def __check_adb_install__():
    tmp_print(mer_title("正在检查ADB安装状态..."))
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

def check_adb(retry_count=1):
    # adb是否安装
    if not __check_adb_install__():
        return False

    try:
        cmd_output = subprocess.check_output(["adb", "devices"], universal_newlines=True, encoding='utf-8')
        devices = re.findall(r"\n(.*?)\tdevice", cmd_output)
        if len(devices) > 1:
            tmp_print("x 只能连接一台手机进行测试, 请断开多余的连接")
            return False

        if devices:
            tmp_print(f"√ 已连接的设备: {', '.join(devices)}")
            return True
        else:
            tmp_print("x 没有android设备连接!")
            return False
    except Exception as e:
        if retry_count > 0:
            tmp_print("x 检查ADB连接时出错，正在尝试重启ADB服务")
            if __restart_adb__():
                # 递归1次
                check_adb(retry_count=retry_count - 1)
        # 大于1或者再次进入except都认为失败
        tmp_print(f"x 重试失败，检查ADB连接时出错: {e}")
        return False

# ---------------------------------------------- minio存储桶状态 ----------------------------------------------
def check_minio():
    tmp_print(mer_title("正在检查minio存储桶状态..."))

    endpoint = 'minio.ecoflow.com:9000'
    access_key = 'EQS4J84JGJCDYNENIMT1'
    secret_key = '8Vgk11c9bDOpZPTJMexPLrxZpzEOqro+jZyAUh+a'

    client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=True)
    try:
        # 检查是否可以列出存储桶
        buckets = client.list_buckets()
        for bucket in buckets:
            tmp_print("√ minio连接成功:", bucket.name)
        return True
    except S3Error as e:
        tmp_print(f"x minio连接出错: {e}")
        return False

def check_phone_wifi(target_wifi="EF-office"):
    tmp_print(mer_title("正在检查手机WiFi状态..."))
    try:
        # 执行ADB命令并获取输出
        result = subprocess.check_output(['adb', 'shell', 'dumpsys netstats | grep -e \'iface=wlan0\'']).decode('utf-8')

        # 使用正则表达式提取wifiNetworkKey的值
        match_wifi_name = re.search('wifiNetworkKey="(.+?)"', result)
        match_network_id = re.search('networkId="(.+?)"', result)
        if match_wifi_name or match_network_id:
            if match_wifi_name:
                wifi_name = match_wifi_name.group(1)
            else:
                wifi_name = match_network_id.group(1)

            # 检查是否为"EF-office"的WiFi
            if wifi_name == target_wifi:
                tmp_print("√ 当前手机已连接EF-office")
                return True
            else:
                tmp_print(f"x 当前手机未连接{target_wifi}, 请将手机连接到{target_wifi}!")
                return False
        else:
            tmp_print("x 没有找到EF-office网络.")
            return False
    except subprocess.CalledProcessError as e:
        tmp_print(f"x 检测EF-office网络出错: {e}")
        return False

def check_nets():
    """
    检查全部环境
    :return:
    """
    target_wifi = "EF-office"
    state_map = {  #
        'state_pc_wifi': [check_pc_wifi(target_wifi), f'tips: 请把本机连接到{target_wifi}!(可能会导致无法运行脚本)'],  # 本机wifi连接
        'state_ecoflow': [check_ecoflow_server(), 'tips: 当前连接后台服务器异常!(可能会导致APP压测数据不准)'],  # 后台连接检测
        'state_google': [check_google(), 'tips: 当前访问外网异常!(可能会导致APP无法配网)'],  # 外网连接检测
        'state_minio': [check_minio(), 'tips: 当前访问minio存储桶异常!(可能会导致无法查看压测数据)'],  # minio存储桶
        'state_adb': [check_adb(), 'tips: 当前连接手机异常!(可能会导致全链路压测无法进行)']  # adb检测
    }
    if state_map['state_adb'][0]:
        # 手机wifi连接
        state_map['state_phone_wifi'] = [check_phone_wifi(target_wifi), f'tips: 请把本机连接到{target_wifi}!(可能会导致APP无法登录)']

    tmp_print('')
    tmp_print('>' * 50)
    tmp_print('环境检测结果如下: ')
    final_state = True
    for state_key, state_value in state_map.items():
        if not state_value[0]:
            final_state = False
            tmp_print(state_value[1])

    if final_state:
        tmp_print('√ 所有测试环境通过!')
    else:
        tmp_print('x 测试环境存在异常!')
    tmp_print('>' * 50)

    return final_state

if __name__ == "__main__":
    envs_state = check_nets()
