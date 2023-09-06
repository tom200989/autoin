import os
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
                return True, [ex.name, ex.install_location, ex.version, ex.uninstall_string]
    return False, None

def check_chromedriver(chrome_install_path):
    """
    查看chrome的安装目录下是否有chromedriver.exe
    :param chrome_install_path:  chrome的安装目录
    :return:  chromedriver.exe的路径
    """
    if chrome_install_path:
        chromedriver_path = os.path.join(chrome_install_path, 'chromedriver.exe')
        if os.path.exists(chromedriver_path):
            return True, chromedriver_path
    return False, None

def check_sdk():
    """
    获取SDK的安装信息
    :return:
    """
    # 拼接SDK路径
    sdk_path = os.path.join(root_dir, 'sdk')
    return os.path.exists(sdk_path)

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

def check_system_envpath():
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
    test_chrome_home = 'C:/Program Files/Google/Chrome/Application'

    # 切割获取到的环境变量
    path_list = system_env_path.split(';')
    test_paths = [
        test_platforms_path,
        test_platform_tools_path,
        test_ndk_path,
        test_jdk_bin_path,
        test_chrome_home
    ]

    # 检查环境变量中是否包含压测的路径
    if all(test_path in path_list for test_path in test_paths):
        # 检查环境变量中压测的路径是否在正确的位置(靠前面的位置)
        indices = [path_list.index(test_path) for test_path in test_paths]
        if all(index < len(test_paths) for index in indices):
            tmp_print('√ 压测编译环境变量配置正确')
            return True
        else:
            tmp_print('x 压测编译环境变量配置异常(未处于优先位置)')
            return False
    else:
        tmp_print('x 压测编译环境变量不全')
        return False

