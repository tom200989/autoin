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

APPIUM_NOT_TARGET_VERSION = -1  # appium版本不是目标版本
APPIUM_NOT_INSTALL = -2  # 未安装appium
APPIUM_ERROR = -3  # appium获取异常
APPIUM_HAD_INSTALL = 1  # 已安装appium

def check_chrome():
    """
    获取chrome的安装信息
    :return:
    """
    return_info = check_exe('google chrome')
    if return_info is not None:
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
    # 此处直接用文件夹是否存在来判断, 不使用 gradle -v 的指令, 因为要切换到gradle目录下才能执行, 而现在需要判断是否安装了gradle
    return is_dir_exits_above_100mb(gradle_dir)

def check_nodejs():
    try:
        # 先切换文件夹到nodejs安装目录下
        os.chdir(nodejs_install_dir)

        # 查询Node.js版本
        node_v = subprocess.getoutput('node --version')
        if '不是内部或外部命令' in node_v:  # 说明没有安装
            tip = 'x node 未安装'
            tmp_print(tip)
            return False, tip, NODE_NOT_INSTALL
        # 版本安装了
        else:
            # 再次检查 - 防止中途在外部被卸载
            exe_infos = check_exe('Node.js')
            if exe_infos is not None:
                node_v = exe_infos[2]
                # 版本匹配(16.18.1)
                if node_target in node_v or node_v in node_target:
                    tmp_print(f'√ node版本：{node_v}')
                # 版本不匹配(16.18.1)
                else:
                    tip = f'x node 当前版本：{node_v}不匹配 (要求:{node_target})'
                    tmp_print(tip)
                    return False, tip, NODE_NOT_TARGET_VERSION
            else:
                tip = 'x node 未安装'
                tmp_print(tip)
                return False, tip, NODE_NOT_INSTALL

        # 查询NPM版本
        npm_version = subprocess.getoutput('npm --version')
        if '不是内部或外部命令' in node_v:  # 说明没有安装
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
    """

    try:
        # 使用 npm list -g --depth=0 查询appium字样是否存在(存在则表明安装了appium)
        # C:\Users\huilin.xu\AppData\Roaming\npm
        # `-- appium@1.22.3

        # 先切换文件夹到nodejs安装目录下
        os.chdir(nodejs_install_dir)

        tmp_print('正在查询npm列表...')
        appium_infos = subprocess.getoutput('npm list -g --depth=0')
        if 'appium@' not in appium_infos:
            tip = 'x appium 未安装'
            tmp_print(tip)
            return False, tip, APPIUM_NOT_INSTALL

        # 如果路径存在(带appium字样)
        else:
            tmp_print('正在检查appium版本...')
            match = re.search(r'appium@([\d.]+)', appium_infos)
            if match:
                # 得到appium版本
                tmp_print('正在获取appium版本...')
                appium_v = match.group(1)
                # 判断版本是否为1.22.3版本
                if appium_target in appium_v or appium_v in appium_target:
                    tip = f'√ appium版本：{appium_v}'
                    tmp_print(tip)
                    return True, tip, APPIUM_HAD_INSTALL
                else:
                    tip = f'x appium版本：{appium_v}不匹配 (要求:{appium_target})'
                    tmp_print(tip)
                    return False, tip, APPIUM_NOT_TARGET_VERSION

        # 其他情况一律认为是获取异常
        tip = f'x appium版本获取失败'
        tmp_print(tip)
        return False, tip, APPIUM_ERROR

    except Exception as e:
        tip = f'x appium版本获取异常：{e}'
        tmp_print(tip)
        return False, tip, APPIUM_ERROR

def check_driver(drivers=None):
    """
    检查驱动是否安装
    :param drivers:
    ch341ser: 芯片日志驱动
    ch343ser: 芯片日志驱动
    slabvcp: 继电器驱动
    """
    if not drivers: drivers = target_driver
    command = ['PnPUtil', '/enum-drivers']
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if stderr:
        tmp_print(stderr.decode('gbk'))
        return False, '驱动检查失败,请重试', []
    else:
        result = stdout.decode('gbk')

        less_drivers = {}
        for key, value in drivers.items():
            if key not in result:
                less_drivers[key] = value

        # 查询哪些驱动没有安装
        if len(less_drivers) > 0:
            driver_list = list(less_drivers.keys())
            tmp_print(f'x 以下驱动没有安装: {driver_list}')
            return False, f'当前驱动{list(less_drivers.keys())}未安装', driver_list
        else:
            tmp_print('驱动检查通过')
            return True, '驱动检查通过', []

def check_system_envpath(chrome_install_path=default_chrome):
    """
    检查系统环境变量中是否配置的是压测的路径
    """
    if chrome_install_path is None: chrome_install_path = default_chrome
    # 获取当前环境变量
    system_env_path = get_env_path()
    # 切割获取到的环境变量
    path_list = system_env_path.split(';')
    # 需要配置的环境变量路径
    test_paths = need_env_paths(chrome_install_path)
    # 检查哪些路径不存在
    missing_paths = [test_path for test_path in test_paths if test_path not in path_list]
    # 单独检测`ANDROID_HOME`和`JAVA_HOME`是否配置
    if 'ANDROID_HOME' not in os.environ:
        missing_paths.append('%ANDROID_HOME%')
    if 'JAVA_HOME' not in os.environ:
        missing_paths.append('%JAVA_HOME%')

    # 如果路径没有缺失
    if len(missing_paths) == 0:
        # 检查路径位置
        indices = [path_list.index(test_path) for test_path in test_paths]
        if all(index < len(test_paths) for index in indices):
            tmp_print('√ 压测编译环境变量配置正确')
            return True, '压测编译环境变量配置正确'
        else:
            tmp_print('x 压测编译环境变量配置异常(未处于优先位置)')
            return False, '压测编译环境变量配置异常(未处于优先位置)'
    else:
        tmp_print('x 压测编译环境变量不全')
        tmp_print(f'缺少以下环境变量: ')
        for miss_path in missing_paths:
            tmp_print(f'x {miss_path}')
        return False, f'压测编译环境变量不全，缺少：{", ".join(missing_paths)}'

# ---------------------------------------------- 检测全部环境 ----------------------------------------------
def check_all_sys():
    """
    检查全部环境
    :return:
    """
    chrome_state, chrome_infos, chrome_tip, _ = check_chrome()
    chrome_install_path = chrome_infos[1] if chrome_infos is not None else default_chrome
    chromedriver_state, chromedriver_path, chromedriver_tip = check_chromedriver(chrome_install_path)
    envs_state, envs_tip = check_system_envpath(chrome_install_path)
    driver_state, driver_tip, _ = check_driver()
    node_state, node_tip, _ = check_nodejs()
    appium_state, appium_tip, _ = check_appium()

    state_map = {  #
        'state_chrome': [chrome_state, f'tips: {chrome_tip}!'],  # chrome安装检测
        'state_chromedriver': [chromedriver_state, f'tips: {chromedriver_tip}!'],  # chromedriver安装检测
        'state_sdk': [check_sdk(), 'tips: 指定SDK环境变量未配置!'],  # SDK环境变量检测
        'state_jdk': [check_jdk(), 'tips: 指定JDK环境变量未配置!'],  # JDK环境变量检测
        'state_ndk': [check_ndk(), 'tips: 指定NDK环境变量未配置!'],  # NDK环境变量检测
        'state_gradle': [check_gradle(), 'tips: 指定GRADLE环境变量未配置!'],  # Gradle环境变量检测
        'state_nodejs': [node_state, f'tips: {node_tip}!'],  # nodejs环境变量检测
        'state_appium': [appium_state, 'tips: appium环境未配置!'],  # appium环境变量检测
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

    return final_state
