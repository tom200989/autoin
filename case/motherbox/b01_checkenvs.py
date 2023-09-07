import os
import re
import subprocess
import winapps
from ctmp_tools import *

def check_chrome():
    """
    获取chrome的安装信息
    :return:
    """
    target_exe = 'google chrome'
    exe = [app.name for app in winapps.search_installed(target_exe)]
    if exe and len(exe) > 0:
        for ex in winapps.list_installed():
            exe_name = str(ex.name).lower()
            if exe_name in target_exe or target_exe in exe_name:
                # chrome名, 安装路径, 版本, 卸载命令
                chrome_name = ex.name
                chrome_install_path = ex.install_location
                chrome_version = ex.version
                chrome_uninstall_string = ex.uninstall_string
                return_info = [chrome_name, chrome_install_path, chrome_version, chrome_uninstall_string]
                # 判断版本是否符合要求
                is_match = bool(re.match(r'^(108|109|110|111|112|113|114)\.', chrome_version))
                if is_match:
                    return True, return_info, "chrome已安装"
                else:
                    return False, return_info, "chrome版本不符合要求(当前只支持108-114版本)"
    return False, [], "未安装chrome"

def check_chromedriver(chrome_install_path):
    """
    查看chrome的安装目录下是否有chromedriver.exe
    :param chrome_install_path:  chrome的安装目录
    :return:  chromedriver.exe的路径
    """
    if chrome_install_path:
        chromedriver_path = os.path.join(chrome_install_path, 'chromedriver.exe')
        if os.path.exists(chromedriver_path):
            return True, chromedriver_path, 'chromedriver已安装'
    return False, None, '未安装chromedriver'

def check_sdk():
    """
    获取SDK的安装信息
    :return:
    """
    # 拼接SDK路径
    sdk_path = os.path.join(root_dir, 'sdk')
    return os.path.exists(sdk_path)

def check_ndk():
    """
    获取NDK的安装信息
    :return:
    """
    # 拼接NDK路径
    ndk_path = os.path.join(root_dir, 'sdk', 'ndk')
    return os.path.exists(ndk_path)

def check_jdk():
    """
    获取JDK的安装信息
    :return:
    """
    # 拼接JDK路径
    jdk_path = os.path.join(root_dir, 'jdk')
    return os.path.exists(jdk_path)

def check_nodejs():
    try:
        # 查询Node.js版本
        state_node = True
        node_version = subprocess.getoutput('node --version')
        if '不是内部或外部命令' in node_version:  # 说明没有安装
            tmp_print('x node 未安装')
            state_node = False
        else:
            tmp_print(f'√ node版本：{node_version}')

        # 查询NPM版本
        state_npm = True
        npm_version = subprocess.getoutput('npm --version')
        if '不是内部或外部命令' in node_version:  # 说明没有安装
            tmp_print('x npm 未安装')
            state_node = False
        else:
            tmp_print(f'√ npm版本：{npm_version}')

        if state_node and state_npm:
            tmp_print(f'√ nodejs 已安装')
            return True
        else:
            return False
    except Exception as e:
        tmp_print(f'x 获取nodejs版本失败：{e}')
        return False

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

def check_system_envpath(chrome_install_path='C:/Program Files/Google/Chrome/Application'):
    """
    检查系统环境变量中是否配置的是压测的路径
    """
    # 获取当前环境变量
    system_env_path = os.getenv('path')
    # SDK路径
    test_sdk_home = os.path.join(root_dir, 'sdk')
    test_platforms_path = os.path.join(test_sdk_home, 'platforms')
    test_platform_tools_path = os.path.join(test_sdk_home, 'platform-tools')
    test_ndk_path = os.path.join(root_dir, 'ndk')
    # JDK路径
    test_jdk_home = os.path.join(root_dir, 'jdk')
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
    chrome_state, chrome_infos, chrome_tip = check_chrome()
    chrome_install_path = chrome_infos[1]
    chromedriver_state, chromedriver_path, chromedriver_tip = check_chromedriver(chrome_install_path)
    envs_state, envs_tip = check_system_envpath(chrome_install_path)

    state_map = {  #
        'state_chrome': [chrome_state, f'tips: {chrome_tip}!'],  # chrome安装检测
        'state_chromedriver': [chromedriver_state, f'tips: {chromedriver_tip}!'],  # chromedriver安装检测
        'state_sdk': [check_sdk(), 'tips: 指定SDK环境变量未配置!'],  # SDK环境变量检测
        'state_jdk': [check_jdk(), 'tips: 指定JDK环境变量未配置!'],  # JDK环境变量检测
        'state_ndk': [check_ndk(), 'tips: 指定NDK环境变量未配置!'],  # NDK环境变量检测
        'state_nodejs': [check_nodejs(), 'tips: nodejs环境未配置!'],  # nodejs环境变量检测
        'state_appium': [check_appium(), 'tips: appium环境未配置!'],  # appium环境变量检测
        'state_envs': [envs_state, f'tips: {envs_tip}!'],  # 系统环境变量检测
    }

    tmp_print('')
    tmp_print('>' * 50)
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
    tmp_print('>' * 50)

# check_all_sys()
