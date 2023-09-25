import os
import re
import subprocess
import winapps
from ctmp_tools import *

CHROME_LOW_VERSION = -1  # chrome版本过低
CHROME_HIGH_VERSION = -2  # chrome版本过高
CHROME_NOT_INSTALL = -3  # 未安装chrome
CHROME_HAD_INSTALL = 1  # 已安装chrome

lowest_version = 108  # 最低支持的chrome版本
highest_version = 119  # 最高支持的chrome版本

NODE_NOT_TARGET_VERSION = -1  # nodejs版本不是目标版本
NODE_NOT_INSTALL = -2  # 未安装nodejs
NPM_NOT_INSTALL = -3  # 未安装npm
NODE_NPM_ERROR = -4  # nodejs和npm获取异常
NODE_NPM_INSTALLED = 1  # 已安装nodejs和npm

def check_chrome():
    """
    获取chrome的安装信息
    :return:
    """
    return_info = check_exe('google chrome')
    if len(return_info) > 0:
        # 获取chrome版本
        chrome_version = return_info[2]
        # 查看chrome版本是否小于108
        if int(chrome_version.split('.')[0]) < lowest_version:
            return False, return_info, f"chrome版本过低(当前只支持{lowest_version}-{highest_version}版本)", CHROME_LOW_VERSION
        elif int(chrome_version.split('.')[0]) > 119:
            return False, return_info, f"chrome版本过高(当前只支持{lowest_version}-{highest_version}版本)", CHROME_HIGH_VERSION
        else:
            return True, return_info, "chrome已安装", CHROME_HAD_INSTALL
    else:
        return False, return_info, "未安装chrome", CHROME_NOT_INSTALL

def check_chromedriver(chrome_install_dir):
    """
    查看chrome的安装目录下是否有chromedriver.exe
    :param chrome_install_dir:  chrome的安装目录
    :return:  chromedriver.exe的路径
    """
    if chrome_install_dir:
        chromedriver_path = os.path.join(chrome_install_dir, 'chromedriver.exe')
        if os.path.exists(chromedriver_path):
            return True, chromedriver_path, 'chromedriver已安装'
    return False, None, '未安装chromedriver'

def check_sdk():
    """
    获取SDK的安装信息
    :return:
    """
    # 拼接SDK路径
    return is_dir_exits_above_100mb(sdk_dir)

def check_ndk():
    """
    获取NDK的安装信息
    :return:
    """
    # 拼接NDK路径
    ndk_path = os.path.join(sdk_dir, 'ndk')
    return is_dir_exits_above_100mb(ndk_path)

def check_jdk():
    """
    获取JDK的安装信息
    :return:
    """
    # 拼接JDK路径
    return is_dir_exits_above_100mb(jdk_dir)

def check_gradle():
    """
    获取Gradle的安装信息
    :return:
    """
    # 拼接Gradle路径
    return is_dir_exits_above_100mb(gradle_dir)

def check_nodejs():
    try:
        # 查询Node.js版本
        node_version = subprocess.getoutput('node --version')
        if '不是内部或外部命令' in node_version:  # 说明没有安装
            tip = 'x node 未安装'
            tmp_print(tip)
            return False, tip, NODE_NOT_INSTALL
        else:
            exe_infos = check_exe('Node.js')
            if len(exe_infos) > 0:
                node_version = exe_infos[2]
                if node_v in node_version or node_version in node_v:
                    tmp_print(f'√ node版本：{node_version}')
                else:
                    tip = f'x node 当前版本：{node_version}不匹配 (要求:{node_v})'
                    tmp_print(tip)
                    return False, tip, NODE_NOT_TARGET_VERSION
            else:
                tip = 'x node 未安装'
                tmp_print(tip)
                return False, tip, NODE_NOT_INSTALL

        # 查询NPM版本
        npm_version = subprocess.getoutput('npm --version')
        if '不是内部或外部命令' in node_version:  # 说明没有安装
            tip = 'x npm 未安装'
            tmp_print(tip)
            return False, tip, NPM_NOT_INSTALL
        else:
            tmp_print(f'√ npm版本：{npm_version}')

        return True, '√ nodejs和npm已安装', NODE_NPM_INSTALLED

    except Exception as e:
        tip = f'x nodejs和npm获取信息异常'
        tmp_print(tip, ":", str(e))
        return False, tip, NODE_NPM_ERROR

def check_appium():
    """
    查询appium是否安装
    :return:
    """
    try:
        # 查询Appium版本
        appium_version = subprocess.getoutput('appium --version')
        if '不是内部或外部命令' in appium_version:
            tmp_print('x appium 未安装')
            return False
        tmp_print(f'√ appium版本：{appium_version}')
        tmp_print(f'√ appium 已安装')
        return True
    except Exception as e:
        tmp_print(f'x 获取appium版本失败：{e}')
        return False

def check_driver(drivers=None):
    """
    检查驱动是否安装
    :param drivers:
    :return:
    """
    if not drivers: drivers = ['CH341SER_A64', 'CH343SER_A64', 'silabser']
    command = ['cmd', '/c', 'driverquery']
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if stderr:
        tmp_print(stderr.decode('gbk'))
        return False, '驱动检查失败,请重试'
    else:
        result = stdout.decode('gbk')
        # 开始切割
        lines = result.split('\n')
        all_modules = [line.split(' ', 1)[0] for line in lines if line]
        # 查询哪些驱动没有安装
        diff = set(drivers) - set(all_modules)
        if diff and len(diff) > 0:
            tmp_print(f'x 以下驱动没有安装: {diff}')
            return False, f'当前驱动{list(diff)}未安装'
        else:
            tmp_print('驱动检查通过')
            return True, '驱动检查通过'

def check_system_envpath(chrome_install_path='C:/Program Files/Google/Chrome/Application'):
    """
    检查系统环境变量中是否配置的是压测的路径
    """
    # 获取当前环境变量
    system_env_path = os.getenv('path')
    # SDK路径
    test_sdk_home = sdk_dir
    test_platforms_path = os.path.join(test_sdk_home, 'platforms')
    test_platform_tools_path = os.path.join(test_sdk_home, 'platform-tools')
    test_ndk_path = os.path.join(root_dir, 'ndk')
    # JDK路径
    test_jdk_home = jdk_dir
    test_jdk_bin_path = os.path.join(test_jdk_home, 'bin')
    # chrome-application路径
    test_chrome_home = chrome_install_path

    # 切割获取到的环境变量
    path_list = system_env_path.split(';')
    test_paths = [test_platforms_path, test_platform_tools_path, test_ndk_path, test_jdk_bin_path, test_chrome_home]

    # 检查环境变量中是否包含压测的路径
    if all(test_path in path_list for test_path in test_paths):
        # 检查环境变量中压测的路径是否在正确的位置(靠前面的位置)
        indices = [path_list.index(test_path) for test_path in test_paths]
        if all(index < len(test_paths) for index in indices):
            tmp_print('√ 压测编译环境变量配置正确')
            return True, '压测编译环境变量配置正确'
        else:
            tmp_print('x 压测编译环境变量配置异常(未处于优先位置)')
            return False, '压测编译环境变量配置异常(未处于优先位置)'
    else:
        tmp_print('x 压测编译环境变量不全')
        return False, '压测编译环境变量不全'

# ---------------------------------------------- 检测全部环境 ----------------------------------------------
def check_all_sys():
    """
    检查全部环境
    :return:
    """
    chrome_state, chrome_infos, chrome_tip, _ = check_chrome()
    chrome_install_path = chrome_infos[1]
    chromedriver_state, chromedriver_path, chromedriver_tip = check_chromedriver(chrome_install_path)
    envs_state, envs_tip = check_system_envpath(chrome_install_path)
    driver_state, driver_tip = check_driver()
    node_state, node_tip, _ = check_nodejs()

    state_map = {  #
        'state_chrome': [chrome_state, f'tips: {chrome_tip}!'],  # chrome安装检测
        'state_chromedriver': [chromedriver_state, f'tips: {chromedriver_tip}!'],  # chromedriver安装检测
        'state_sdk': [check_sdk(), 'tips: 指定SDK环境变量未配置!'],  # SDK环境变量检测
        'state_jdk': [check_jdk(), 'tips: 指定JDK环境变量未配置!'],  # JDK环境变量检测
        'state_ndk': [check_ndk(), 'tips: 指定NDK环境变量未配置!'],  # NDK环境变量检测
        'state_gradle': [check_gradle(), 'tips: 指定GRADLE环境变量未配置!'],  # Gradle环境变量检测
        'state_nodejs': [node_state, f'tips: {node_tip}!'],  # nodejs环境变量检测
        'state_appium': [check_appium(), 'tips: appium环境未配置!'],  # appium环境变量检测
        'state_driver': [driver_state, f'tips: {driver_tip}!'],  # appium环境变量检测
        'state_envs': [envs_state, f'tips: {envs_tip}!'],  # 系统环境变量检测
    }

    tmp_print('')
    tmp_print('>' * 80)
    tmp_print('系统环境检测结果如下: ')
    final_state = True
    for state_key, state_value in state_map.items():
        if not state_value[0]:
            final_state = False
            tmp_print(state_value[1])

    if final_state:
        tmp_print('√ 所有系统环境测试通过!')
    else:
        tmp_print('x 系统环境测试不通过!')
    tmp_print('>' * 80)
