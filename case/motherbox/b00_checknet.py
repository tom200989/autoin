from cminio_tools import *
from ctmp_tools import *

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

# ---------------------------------------------- 后台环境状态 ----------------------------------------------
def check_ecoflow_server():
    # 检查atrust是否打开
    is_atrust = is_process_running('aTrustTray.exe')
    if not is_atrust:
        tmp_print("x [ecoflow]aTrustTray未打开, 请手动打开aTrustTray并确保其处于登录状态!")
        return False
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
            response = requests.get(url, timeout=30)
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
            if 'timed out' in str(e):
                tmp_print(f"x {key} 连接超时")
            else:
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
    # 检查atrust是否打开
    is_atrust = is_process_running('aTrustTray.exe')
    if not is_atrust:
        tmp_print("x [google]aTrustTray未打开, 请手动打开aTrustTray并确保其处于登录状态!")
        return False

    urls = ["https://www.google.com"]
    for url in urls:
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                tmp_print(f"√ 本机连接外网正常")
                return True
            else:
                tmp_print(f"x {url} 本机连接异常({response.status_code})")
                return False
        except Exception as e:
            if 'timed out' in str(e):
                tmp_print(f"x {url} 本机连接超时")
            else:
                tmp_print(f"x {url} 本机连接失败: {e}")
            return False

# ---------------------------------------------- adb连接状态 ----------------------------------------------
def check_adb(retry_count=1):
    # adb是否安装
    if not check_adb_install():
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
            if restart_adb():
                # 递归1次
                check_adb(retry_count=retry_count - 1)
        # 大于1或者再次进入except都认为失败
        tmp_print(f"x 重试失败，检查ADB连接时出错: {e}")
        return False

# ---------------------------------------------- 手机版本 ----------------------------------------------
def check_phone():
    """
    检查手机SDK版本
    :return: 手机sdk版本
    """
    try:
        # 执行adb命令获取Android SDK版本
        result = subprocess.check_output(["adb", "shell", "getprop", "ro.build.version.sdk"], stderr=subprocess.STDOUT, encoding='utf-8')
        sdk_version = int(result.strip())  # 转换为整数
        # 只支持Android 24到33
        if sdk_version < 24:
            tip = f"x 手机SDK版本过低(Android SDK {sdk_version}), 请使用Android 7以上(含Android 7)的原生手机"
            tmp_print(tip)
            return False, sdk_version, tip
        if sdk_version > 33:
            tip = f"x 手机SDK版本过高(Android SDK {sdk_version}), 请使用Android 14以下(不含Android 14)的原生手机"
            tmp_print(tip)
            return False, sdk_version, tip

        tip = f"√ 手机SDK版本已匹配: {sdk_version}"
        tmp_print(tip)
        return True, sdk_version, tip
    except Exception as e:
        tip = f"x 获取手机版本出错: {e}"
        tmp_print(tip)
        return False, tip

# ---------------------------------------------- minio存储桶状态 ----------------------------------------------
def check_minio():
    # 检查atrust是否打开
    is_atrust = is_process_running('aTrustTray.exe')
    if not is_atrust:
        tmp_print("x [minio]aTrustTray未打开, 请手动打开aTrustTray并确保其处于登录状态!")
        return False
    # 检查minio连接
    minio_state, minio_tip, _ = check_minio_connect()
    if minio_state:
        tmp_print(f"√ minio连接成功:{minio_tip}")
        return True
    else:
        tmp_print(f"x minio连接出错: {minio_tip}")
        return False

# ---------------------------------------------- 手机wifi状态 ----------------------------------------------
def check_phone_wifi(target_wifi="EF-office"):
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

# ---------------------------------------------- 检查全部环境 ----------------------------------------------
def check_all_nets(is_need_adb=True):
    """
    检查全部环境
    @param is_need_adb: 是否检查adb连接(默认检查)
    """
    target_wifi = "EF-office"
    is_adb = check_adb()
    state_map = {  #
        'state_pc_wifi': [check_pc_wifi(target_wifi), f'tips: 请把本机连接到{target_wifi}!(可能会导致无法运行脚本)'],  # 本机wifi连接
        'state_ecoflow': [check_ecoflow_server(), 'tips: 当前连接后台服务器异常!(可能会导致APP压测数据不准)'],  # 后台连接检测
        'state_google': [check_google(), 'tips: 当前访问外网异常!(可能会导致APP无法配网)'],  # 外网连接检测
        'state_minio': [check_minio(), 'tips: 当前访问minio存储桶异常!(可能会导致无法查看压测数据,请检查atrust是否已经开启并已登录)'],  # minio存储桶
        'state_adb': [is_adb, 'tips: 当前连接手机异常!(可能会导致全链路压测无法进行)']  # adb检测
    }
    if is_adb:
        # 手机wifi连接
        state_map['state_phone_wifi'] = [check_phone_wifi(target_wifi), f'tips: 请把本机连接到{target_wifi}!(可能会导致APP无法登录)']
        # 手机版本
        is_phone,phone_v, phone_tip = check_phone()
        state_map['state_phone'] =[is_phone, f'tips: {phone_tip}']  # 手机检测


    tmp_print('')
    tmp_print('>' * 80)
    tmp_print('网络环境检测结果如下: ')
    final_state = True
    for state_key, state_value in state_map.items():
        # 如果不检查adb连接, 则跳过
        if state_key == 'state_adb' and not is_need_adb:
            continue
        if not state_value[0]:
            final_state = False
            tmp_print(state_value[1])

    if final_state:
        tmp_print('√ 测试网络环境通过!')
    else:
        tmp_print('x 测试网络环境异常!')
    tmp_print('>' * 80)

    return final_state

def check_pingnet(is_minio=True):
    """
    仅检测网络连通性
    @param is_minio: 是否检查minio存储桶(默认检查)
                     如果是只运行本地的测试用例, 则不需要检查minio存储桶, 发飞书时再检查
    :return: True 网络连通, False 网络不通
    """
    target_wifi = "EF-office"
    state_map = {  #
        'state_pc_wifi': [check_pc_wifi(target_wifi), f'tips: 请把本机连接到{target_wifi}!(可能会导致无法运行脚本)'],  # 本机wifi连接
        'state_google': [check_google(), 'tips: 当前访问外网异常!(可能会导致APP无法配网)'],  # 外网连接检测
    }
    # 如果需要检查minio存储桶, 则添加
    if is_minio:
        state_map['state_minio'] = [check_minio(), 'tips: 当前访问minio存储桶异常!(可能会导致无法查看压测数据,请检查atrust是否已经开启并已登录)']  # minio存储桶

    tmp_print('')
    tmp_print('>' * 80)
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
    tmp_print('>' * 80)

    return final_state
