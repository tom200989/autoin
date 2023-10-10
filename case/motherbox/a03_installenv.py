import os
import shutil

from b00_checknet import *
from b01_checkenvs import *

""" ----------------------------------------------- 基础操作 ----------------------------------------------- """

def __checkdown_chromedriver():
    """
    检查chromedriver是否下载
    :return:
    """
    chrome_state, chrome_infos, chrome_tip, chrome_version_state = check_chrome()
    if chrome_infos is not None:
        # 获取chrome版本(如117)和安装路径
        chrome_v = str(chrome_infos[2]).split('.')[0]
        chrome_install_dir = str(chrome_infos[1])
        tmp_print(f'当前chrome版本: {chrome_v}')
        tmp_print(f'当前chrome安装路径: {chrome_install_dir}')
        # 检查Application目录下是否有chromedriver.exe
        state, driver_path, tip = check_chromedriver(chrome_install_dir)
        if state:
            tmp_print('√ chromedriver已安装')
            return True
        else:
            tmp_print('chromedriver未安装, 准备开始下载...')
            # 检查网络是否畅通
            is_network = check_pingnet()
            if not is_network: return False
            # 从minio查询chromedriver现有版本
            temp_drs = {}
            minio_chromedrivers = list_minio_objs(minio_chromedriver_root)
            if minio_chromedrivers is None:
                tmp_print('x 远端数据库异常,chromedriver不存在, 请联系管理员')
                return False
            # 如果minio数据库正常
            for cdp in minio_chromedrivers:
                # {'117': 'autocase/android/env/chromes/chromedriver/chromedriver_117.zip'}
                temp_drs[cdp[str(cdp).rfind('/') + 1:].split('_')[1].split('.')[0]] = cdp
            # 判断是否有对应版本的chromedriver
            if chrome_v in list(temp_drs.keys()):
                tmp_print('查找到数据库存在当前chrome版本的driver, 准备下载...')
                # 获取对应版本的chromedriver的minio路径
                chromedriver_path = temp_drs[chrome_v]  # '/autocase/android/env/chromes/chromedriver/chromedriver_117.zip'

            else:
                tmp_print(f'数据库中未找到当前chrome版本[{chrome_v}]的driver, 将下载数据库最近版本, 可能影响使用.')
                # 获取数据库中最大的版本号的chromedriver的minio路径
                chromedriver_path = max(list(map(int, list(temp_drs.keys()))))

            # 截取chromedriver的文件名
            chromedriver_zipname = chromedriver_path[chromedriver_path.rfind('/') + 1:]  # 'chromedriver_117.zip'
            driver_zippath = os.path.join(chrome_install_dir, chromedriver_zipname)  # 'C:/Program Files/Google/Chrome/Application/chromedriver_117.zip'
            tmp_print(f'即将下载chromedriver到: {driver_zippath}...')
            # 先删除旧的chromedriver
            tmp_print('正在删除旧的chromedriver...')
            if os.path.exists(str(driver_path)): os.remove(str(driver_path))  # 删除旧的chromedriver.exe
            if os.path.exists(str(driver_zippath)): os.remove(str(driver_zippath))  # 删除旧的chromedriver.zip
            # 下载chromedriver
            tmp_print('正在下载chromedriver...')
            download_obj(driver_zippath, chromedriver_path)
            # 解压chromedriver
            tmp_print('正在解压chromedriver...')
            shutil.unpack_archive(driver_zippath, chrome_install_dir)
            # 删除压缩包
            tmp_print('正在删除压缩包...')
            os.remove(str(driver_zippath))
            # 把解压后的 chromedriver.exe 和 LICENSE.chromedriver 移动到chrome/Application目录下
            tmp_print('正在移动解压后的文件...')
            files_to_move = ["chromedriver.exe", "LICENSE.chromedriver"]
            # 遍历目标目录下的所有子目录
            for sub_dir in os.listdir(chrome_install_dir):
                # 拼接子目录的完整路径 (C:/Program Files/Google/Chrome/Application/xxx)
                sub_dir_path = os.path.join(chrome_install_dir, sub_dir)
                # 检查是否为目录以及名称是否包含'chromedriver'
                if os.path.isdir(sub_dir_path) and 'chromedriver' in sub_dir.lower():
                    tmp_print(f"找到 {sub_dir_path} 目录.")
                    # 移动文件
                    for f in files_to_move:
                        src_path = os.path.join(sub_dir_path, f)
                        if not os.path.exists(src_path): continue
                        dest_path = os.path.join(chrome_install_dir, f)
                        shutil.move(src_path, dest_path)
                        tmp_print(f"已移动 {f} 到 {chrome_install_dir}.")
                    # 删除子目录
                    shutil.rmtree(sub_dir_path)
                    tmp_print(f"已删除 {sub_dir_path} 目录.")

            tmp_print('√ chromedriver安装完成')
            return True
    else:
        tmp_print('x 未安装chrome,请重试')
        return False

def __reinstall_chrome(chrome_infos=None):
    """
    重装chrome
    :param chrome_infos: 如果为None,则直接安装(无需卸载)
    """
    try:
        # 检查网络是否畅通
        is_network = check_pingnet()
        if not is_network: return False
        # 先清空并删除ChromeSetup目录
        if os.path.exists(str(chromesetup_dir)): shutil.rmtree(chromesetup_dir, onerror=del_rw)
        # 再重新创建ChromeSetup目录
        os.makedirs(chromesetup_dir)
        # 如果传入了chrome_infos(说明原先已安装), 则先卸载
        if chrome_infos is not None:
            uninst_state = _uninstall_chrome(chrome_infos)
            if not uninst_state: return False
        # 从Minio下载chrome安装包
        tmp_print('正在下载chrome安装包...')
        chromesetup_path = os.path.join(chromesetup_dir, 'ChromeSetup.zip')
        download_obj(chromesetup_path, minio_chrome_zip)
        # 解压安装包
        tmp_print('正在解压安装包...')
        shutil.unpack_archive(chromesetup_path, chromesetup_dir)
        # 删除压缩包
        tmp_print('正在删除压缩包...')
        os.remove(str(chromesetup_path))
        # 安装chrome
        tmp_print('正在重新安装chrome...')
        chromesetup_exe = os.path.join(chromesetup_dir, 'ChromeSetup.exe')
        subprocess.run(chromesetup_exe, shell=True)
        # 监听安装进度
        temp_tick = 0
        while is_process_running('ChromeSetup.exe'):
            time.sleep(1)
            temp_tick += 1
            tmp_print(f'正在安装chrome...{temp_tick}s')
        # 查询chrome版本
        chrome_state, chrome_infos, chrome_tip, chrome_version_state = check_chrome()
        tmp_print(f'Chrome 安装完成, 当前版本为: {chrome_infos[2]}')
        # 此时chrome会自动打开, 等待3秒, 直接关闭
        time.sleep(3)
        kill_exe('chrome.exe')
        return True

    except Exception as e:
        tmp_print(f'重装chrome失败, 发生错误: {e}')
        return False

def __reinstall_node(direct_install=False):
    """
    重装node
    @param direct_install: 是否直接安装, 默认为False, 即先卸载再安装
    """
    # 检查网络是否正常
    is_network = check_pingnet()
    if not is_network:
        tmp_print('x 网络异常, 请检查网络')
        return False

    node_infos = check_exe('Node.js')
    # 先卸载 (如果不是直接安裝)
    if not direct_install:
        # 也要先判断下是否需要卸载
        if node_infos is not None:
            uninst_state = _uninstall_nodejs(node_infos)
            if not uninst_state: return False

    # 安装
    # 先清除nodejs目录
    tmp_print('正在清除nodejs目录...')
    if os.path.exists(str(nodejs_dir)):
        shutil.rmtree(nodejs_dir, onerror=del_rw)
        time.sleep(2)
    # 从Minio下载msi安装包
    tmp_print('正在下载nodejs安装包...')
    nodejs_zip = os.path.join(nodejs_dir, 'nodejs.zip')
    download_obj(nodejs_zip, minio_nodejs)
    # 解压安装包
    tmp_print('正在解压安装包...')
    shutil.unpack_archive(nodejs_zip, nodejs_dir)
    # 删除压缩包
    tmp_print('正在删除压缩包...')
    os.remove(str(nodejs_zip))
    # 安装nodejs
    tmp_print('正在安装nodejs...')
    nodejs_msi_path = os.path.join(nodejs_dir, 'nodejs.msi')
    # 把斜杠转换为反斜杠
    nodejs_msi_path = nodejs_msi_path.replace('/', '\\')
    install_command = f'msiexec /i {nodejs_msi_path} /q'
    tmp_print(install_command)
    try:
        # 执行静默安装
        subprocess.run(install_command, shell=True, check=True)
        time.sleep(5)
        new_infos = check_exe('Node.js')
        if new_infos is not None:
            new_node_v = [2]
            tmp_print(f'成功安装 Node.js({new_node_v})')
            return True
        else:
            tmp_print('x 安装后未检测到Node.js, 安装失败')
            return False
    except Exception as e:
        tmp_print(f'安装Node.js失败: {e}')
        return False

def __reinstall_appium(direct_install=False):
    """
    重装appium
    :param direct_install:  是否直接安装, 默认为False, 即先卸载再安装
    """
    # 检查网络是否正常
    is_network = check_pingnet()
    if not is_network:
        tmp_print('x 网络异常, 请检查网络')
        return False

    # 卸载
    if not direct_install:
        uninst_state = _uninstall_appium()
        if not uninst_state: return False

    # 安装
    tmp_print('正在安装 Appium...')
    install_cmd = 'npm --registry http://registry.npm.taobao.org install appium@1.22.3 -g --no-optional --no-audit --no-fund'
    tmp_print(install_cmd)
    try:
        # 执行安装
        subprocess.run(install_cmd, shell=True, check=True)
        time.sleep(5)
        appium_v = 'unknown(未能获取安装后的版本)'
        appium_infos = subprocess.getoutput('npm list -g --depth=0')
        if 'appium@' in appium_infos:
            match = re.search(r'appium@([\d.]+)', appium_infos)
            if match: appium_v = match.group(1)
        tmp_print(f'Appium 安装完成, 当前版本为: {appium_v}')
        return True
    except Exception as e:
        tmp_print(f'安装Appium失败: {e}')
        return False

""" ----------------------------------------------- 卸载各步骤 ----------------------------------------------- """

def _uninstall_chrome(chrome_infos=None):
    """
    卸载chrome
    :param chrome_infos: 外部传入的chrome安装信息(复用)
    """
    # 1.检查chrome安装状态
    # chrome_state: True 已安装, False 未安装
    # chrome_infos: chrome的安装信息
    # chrome_tip: chrome的安装提示
    # chrome_version_state: chrome版本状态(-1:过低,-2:过高,-3:未安装,-4:已安装)

    # 如果外部传入的infos为空(一键卸载), 则内部自己检查
    try:
        tmp_print('=' * 30, '>>> 开始卸载Chrome...', '=' * 30, )
        # 结束chrome进程
        tmp_print('正在关闭chrome...')
        kill_exe('chrome.exe')

        # 这里是提供给重装时复用的判断
        if chrome_infos is None:
            chrome_state, chrome_infos, chrome_tip, chrome_version_state = check_chrome()

        if chrome_infos is not None:
            # 开始卸载
            tmp_print('正在卸载chrome...')
            # 在chrome_infos中查找卸载命令
            uninstall_cmd = next((str(item) for item in chrome_infos if '--uninstall' in str(item)), None)
            # 拼接强制卸载参数
            uninstall_cmd = uninstall_cmd + ' --force-uninstall'
            tmp_print(uninstall_cmd)
            # 执行卸载命令, 先卸载
            subprocess.run(uninstall_cmd, shell=True)
            time.sleep(5)
            tmp_print('Chrome 卸载完成')

            # 删除chromedriver
            tmp_print('正在删除chromedriver...')
            chrome_install_dir = str(chrome_infos[1])  # xx/Application
            chromedriver_path = os.path.join(chrome_install_dir, 'chromedriver.exe')
            if os.path.exists(str(chromedriver_path)): os.remove(str(chromedriver_path))
            tmp_print('chromedriver删除成功')
            return True
        else:
            tmp_print('本PC未检测到chrome, 无需卸载')
            return True
    except Exception as e:
        tmp_print(f"卸载chrome失败, 发生错误: {e}")
        return False

def _uninstall_sdk_jdk_gradle():
    """
    直接删除autocase总目录
    """
    tmp_print('=' * 30, '>>> 开始卸载压测目录...', '=' * 30)
    if os.path.exists(root_dir):
        for cdir in uninst_dirs:
            if os.path.exists(str(cdir)):
                try:
                    shutil.rmtree(cdir, onerror=del_rw)
                    tmp_print(f'{cdir}删除成功')
                except Exception as e:
                    tmp_print(f'x {cdir}删除失败, 发生错误: {e}')
            else:
                tmp_print(f'{cdir}不存在, 无需删除')
        tmp_print('全部压测目录删除完成')
        return True
    else:
        tmp_print('总目录不存在, 无需卸载')
        return True

def _uninstall_nodejs(node_infos=None):
    """
    卸载nodejs
    :param node_infos: 外部传入的nodejs安装信息(复用)
    """
    try:
        tmp_print('=' * 30, '>>> 开始卸载Nodejs...', '=' * 30)
        # 结束node进程
        tmp_print('正在关闭node...')
        kill_exe('node.exe')

        # 如果外部传入的infos为空(一键卸载), 则内部自己检查
        if node_infos is None:
            node_infos = check_exe('Node.js')

        if node_infos is not None:
            # 先卸载
            tmp_print('正在卸载 Node.js...')
            # 在node_infos中查找卸载命令(此处的索引可能会随着项目的迭代而变化)
            uninstall_cmd = node_infos[3]
            # 修改指令参数 (把/I修改为/x, 后边跟随/q以静默卸载)
            uninstall_cmd = uninstall_cmd.replace('/I', '/x').replace('/i', '/x') + ' /q'
            tmp_print(uninstall_cmd)
            # 执行卸载命令, 先卸载
            subprocess.run(uninstall_cmd, shell=True)
            time.sleep(2)
            tmp_print('Node.js 卸载完成')
            return True
        else:
            tmp_print('本PC未检测到Node.js, 无需卸载')
            return True
    except Exception as e:
        tmp_print(f'卸载Node.js失败, 发生错误: {e}')
        return False

def _uninstall_appium():
    """
    卸载appium
    """
    try:
        tmp_print('=' * 30, '>>> 开始卸载Appium...', '=' * 30)

        # 关闭appium
        tmp_print('正在关闭appium...')
        port_infos = check_port()  # info = [occupy, str(result), port, int(pid)]
        occupy = port_infos[0]
        port = port_infos[2]
        pid = port_infos[3]
        if occupy: kill_port(port, pid)
        # 结束node进程
        tmp_print('正在关闭node...')
        kill_exe('node.exe')
        # 开始卸载
        tmp_print('正在卸载 Appium...')
        tmp_print('执行指令: npm uninstall appium -g')
        subprocess.run('npm uninstall appium -g', shell=True)
        time.sleep(5)
        tmp_print('Appium 卸载完成')
        return True
    except Exception as e:
        tmp_print(f'卸载Appium失败, 发生错误: {e}')
        return False

def _uninstall_driver(driver_names):
    """
    卸载驱动
    :param driver_names: 驱动名列表
    """
    tmp_print('=' * 30, '>>> 开始卸载驱动...', '=' * 30)
    # 执行PnPUtil命令并获取输出结果
    cmd_output = subprocess.check_output('PnPUtil /enum-drivers', shell=True, text=True)
    # 把多行字符串拆成行列表
    lines = cmd_output.split("\n")
    for driver_name in driver_names:
        # 初始化发布名称
        publish_name = None
        # 遍历行列表
        for i, line in enumerate(lines):
            # 如果找到了目标字符串
            if f"{driver_name.lower()}" in line.lower():
                # 取前一行，获取发布名称
                publish_name = lines[i - 1].split(":")[1].strip()
                break

        # 输出结果
        if publish_name:
            tmp_print(f"找到匹配项，发布名称为: {publish_name}")
            # 开始卸载
            subprocess.run(f"PnPUtil /delete-driver {publish_name} /uninstall", shell=True, check=True)
            tmp_print("卸载成功")
        else:
            tmp_print(f"未找到驱动: {driver_name}")

    # 再次检查
    un_state, un_tip, un_list = check_driver()
    if un_state:  # 如果还能检查出驱动
        tmp_print(f'x 驱动卸载失败, {un_list}未卸载干净')
        return False
    elif not un_state and not '驱动检查失败' in un_tip:  # 如果状态为False, 且没有`驱动检查失败`的提示 - 就认为卸载成功
        tmp_print('√ 全部驱动卸载完成')
        # 删除驱动总目录(D:/autocase/driver)
        if os.path.exists(str(driver_dir)):
            tmp_print('正在删除驱动总目录...')
            shutil.rmtree(driver_dir, onerror=del_rw)
            tmp_print('√ 驱动总目录删除成功')
        return True
    else:
        tmp_print(f'x 驱动卸载异常')
        return False

def _restore_sys_envs():
    tmp_print('=' * 30, '>>> 开始还原系统变量...', '=' * 30)
    return restore_envs()

""" ----------------------------------------------- 安装各步骤 ----------------------------------------------- """

def _install_chrome():
    """
    安装chrome
    :return:  True 安装成功, False 安装失败
    """
    # 检查网络是否正常
    is_network = check_pingnet()
    if not is_network:
        tmp_print('x 网络异常, 请检查网络')
        return False

    # 0.结束chrome进程
    kill_exe('chrome.exe')
    kill_exe('chromedriver.exe')

    # 1.检查chrome安装状态
    # chrome_state: True 已安装, False 未安装
    # chrome_infos: chrome的安装信息
    # chrome_tip: chrome的安装提示
    # chrome_version_state: chrome版本状态(-1:过低,-2:过高,-3:未安装,-4:已安装)
    chrome_state, chrome_infos, chrome_tip, chrome_version_state = check_chrome()

    # chrome重装状态
    chrome_reinstall_state = False
    # 2.如果版本过低或者过高, 则重装chrome
    if chrome_version_state == CHROME_LOW_VERSION or chrome_version_state == CHROME_HIGH_VERSION:
        chrome_reinstall_state = __reinstall_chrome(chrome_infos)
    # 2.1.如果未安装chrome, 则安装chrome
    elif chrome_version_state == CHROME_NOT_INSTALL:
        chrome_reinstall_state = __reinstall_chrome()
    elif chrome_version_state == CHROME_HAD_INSTALL:
        chrome_reinstall_state = True

    if not chrome_reinstall_state:
        tmp_print('x 未检测到可用的chrome, 请重试')
        return False

    # 3.以上步骤完毕 - 检查chromedriver
    chromedriver_install_state = __checkdown_chromedriver()
    return chromedriver_install_state

def _install_sdk_jdk_gradle():
    """
    安装SDK/JDK/GRADLE
    """
    sdk_i, jdk_i, gradle_i = False, False, False

    # 1.检查SDK是否安装
    sdk_state = check_sdk()
    # 2.检查JDK是否安装
    jdk_state = check_jdk()
    # 3.检查Gradle是否安装
    gradle_state = check_gradle()
    # 4.检查网络是否畅通
    is_network = check_pingnet()
    if not is_network:
        tmp_print('x 网络异常, 请检查网络')
        return False
    # 5.如果SDK和JDK都已安装, 则跳过
    try:
        if sdk_state:
            tmp_print('√ SDK已安装')
        else:
            # 删除原来的SDK
            tmp_print('正在删除原来的SDK...')
            if os.path.exists(str(sdk_dir)):
                shutil.rmtree(sdk_dir, onerror=del_rw)
                time.sleep(2)
            # 下载SDK
            tmp_print('正在下载SDK...')
            sdk_local_zip = os.path.join(sdk_dir, 'sdk.zip')
            download_obj(sdk_local_zip, minio_sdk)
            # 解压SDK
            tmp_print('正在解压SDK...')
            shutil.unpack_archive(str(sdk_local_zip), sdk_dir)
            time.sleep(1)
            # 删除压缩包
            tmp_print('正在删除压缩包...')
            os.remove(str(sdk_local_zip))

        sdk_i = True
    except Exception as e:
        tmp_print(f'安装SDK失败, 发生错误: {e}')
        sdk_i = False

    try:
        if jdk_state:
            tmp_print('√ JDK已安装')
        else:
            # 删除原来的JDK
            tmp_print('正在删除原来的JDK...')
            if os.path.exists(str(jdk_dir)):
                shutil.rmtree(jdk_dir, onerror=del_rw)
                time.sleep(2)
            # 下载JDK
            tmp_print('正在下载JDK...')
            jdk_local_zip = os.path.join(jdk_dir, 'jdk.zip')
            download_obj(jdk_local_zip, minio_jdk)
            # 解压JDK
            tmp_print('正在解压JDK...')
            shutil.unpack_archive(str(jdk_local_zip), jdk_dir)
            time.sleep(1)
            # 删除压缩包
            tmp_print('正在删除压缩包...')
            os.remove(str(jdk_local_zip))

        jdk_i = True
    except Exception as e:
        tmp_print(f'安装JDK失败, 发生错误: {e}')
        jdk_i = False

    try:
        if gradle_state:
            tmp_print('√ Gradle已安装')
        else:
            # 删除原来的Gradle
            tmp_print('正在删除原来的Gradle...')
            if os.path.exists(str(gradle_dir)):
                shutil.rmtree(gradle_dir, onerror=del_rw)
                time.sleep(2)
            # 下载Gradle
            tmp_print('正在下载Gradle...')
            gradle_local_zip = os.path.join(gradle_dir, 'gradle.zip')
            download_obj(gradle_local_zip, minio_gradle)
            # 解压Gradle
            tmp_print('正在解压Gradle...')
            shutil.unpack_archive(str(gradle_local_zip), gradle_dir)
            time.sleep(1)
            # 删除压缩包
            tmp_print('正在删除压缩包...')
            os.remove(str(gradle_local_zip))

        gradle_i = True
    except Exception as e:
        tmp_print(f'安装Gradle失败, 发生错误: {e}')
        gradle_i = False

    all_i = sdk_i and jdk_i and gradle_i
    if all_i:
        tmp_print('√ SDK/JDK/Gradle全部已安装')

    return all_i

def _install_nodejs():
    """
    安装nodejs
    :return:
    """
    # 检查网络是否正常
    is_network = check_pingnet()
    if not is_network:
        tmp_print('x 网络异常, 请检查网络')
        return False
    node_state, node_tip, node_type = check_nodejs()
    if not node_state:  # 不符合要求
        # 判断类型
        if node_type == NODE_NOT_INSTALL:
            tmp_print('未安装nodejs, 准备开始安装...')
            return __reinstall_node(True)  # 直接安裝
        elif node_type == NODE_NOT_TARGET_VERSION:
            tmp_print('nodejs版本不匹配, 准备开始重新安装...')
            return __reinstall_node()  # 先卸载再安装
        elif node_type == NPM_NOT_INSTALL:
            tmp_print('npm未安装, 准备开始重新安装...')
            return __reinstall_node()  # 先卸载再安装
        elif node_type == NODE_NPM_ERROR:
            tmp_print('nodejs和npm获取信息异常, 准备开始重新安装...')
            return __reinstall_node()  # 先卸载再安装
        else:
            tmp_print('nodejs已安装, 无需重装')
            return True
    else:
        tmp_print('nodejs已安装且符合要求, 无需重装')
        return True

def _install_appium():
    """
    安装appium
    :return:
    """
    # 检查网络是否正常
    is_network = check_pingnet()
    if not is_network:
        tmp_print('x 网络异常, 请检查网络')
        return False

    appium_state, appium_tip, appium_type = check_appium()
    if not appium_state:  # 不符合要求
        if appium_type == APPIUM_HAD_INSTALL:
            tmp_print('√ appium已安装且符合要求, 无需重装')
            return True
        elif appium_type == APPIUM_NOT_INSTALL:
            tmp_print('appium未安装, 准备开始安装...')
            return __reinstall_appium(True)  # 直接安装
        elif appium_type == APPIUM_NOT_TARGET_VERSION:
            tmp_print('appium版本非指定版本, 即将重新安装...')
            return __reinstall_appium()  # 先卸载再安装
        elif appium_type == APPIUM_ERROR:
            tmp_print('检测appium版本出错, 即将重新安装...')
            return __reinstall_appium()  # 先卸载再安装
    else:  # 符合要求
        tmp_print('√ appium已安装且符合要求, 无需重装')
        return True

def _install_driver(retry=0):
    # 检查网络是否正常
    is_network = check_pingnet()
    if not is_network:
        tmp_print('x 网络异常, 请检查网络')
        return False
    try:
        # 检查哪个驱动未安装
        d_state, d_tip, d_uninstall = check_driver()
        if d_uninstall and len(d_uninstall) > 0:
            # 说明有驱动未安装
            tmp_print(f'{d_uninstall}驱动未安装, 即将开始安装...')

            # minio下载驱动
            for d_u in d_uninstall:
                # 截取驱动名 ch341ser.inf -> ch341ser
                d_name = d_u[:d_u.rfind('.')].lower()
                # 从 minio下载 D:/autocase/driver/ch341ser/ch341ser.zip -- autocase/android/env/driver/ch341ser.zip
                local_driver_x_dir = os.path.join(driver_dir, d_name)  # 单个驱动目录
                if os.path.exists(str(local_driver_x_dir)): shutil.rmtree(local_driver_x_dir, onerror=del_rw)  # 先删除旧的驱动
                os.makedirs(local_driver_x_dir)  # 再创建新的驱动目录
                local_driver_zip = os.path.join(driver_dir, d_name, f'{d_name}.zip')  # 创建压缩包
                minio_driver = minio_driver_root + d_name + '.zip'  # minio下载驱动路径
                download_obj(local_driver_zip, minio_driver)  # 开始下载
                time.sleep(3)

            # 解压驱动
            for d_u in d_uninstall:
                # 截取驱动名 ch341ser.inf -> ch341ser
                d_name = d_u[:d_u.rfind('.')].lower()
                # 解压驱动
                tmp_print(f'正在解压驱动: {d_name}...')
                local_driver_zip = os.path.join(driver_dir, d_name, f'{d_name}.zip')
                shutil.unpack_archive(local_driver_zip, os.path.join(driver_dir, d_name))
                # 删除压缩包
                tmp_print(f'正在删除压缩包: {d_name}...')
                os.remove(str(local_driver_zip))

            # 安装驱动
            for d_u in d_uninstall:
                # 截取驱动名 ch341ser.inf -> ch341ser
                d_name = d_u[:d_u.rfind('.')].lower()
                # 安装驱动
                tmp_print(f'正在安装驱动: {d_name}...')
                local_driver_dir = os.path.join(driver_dir, d_name)
                if 'ch343ser' in d_name or d_name in 'ch343ser':  # 如果是ch343ser驱动, 则需要进入Driver目录
                    local_driver_dir = os.path.join(local_driver_dir, 'Driver')
                # 拼接驱动安装指令
                install_cmd = f'PnPUtil /add-driver {local_driver_dir}/{d_u} /install'
                tmp_print(install_cmd)
                # 执行安装指令
                subprocess.run(install_cmd, shell=True, text=True, check=True)
                time.sleep(2)

            # 再次检查
            new_state, new_tip, new_uninstall = check_driver()
            if new_state:
                tmp_print('√ 所需驱动全部安装完成')
                return True
            else:
                if retry <= 0:  # 如果重试次数小于等于0, 进行重试
                    tmp_print('x 驱动安装失败, 正在重试...')
                    is_un = _uninstall_driver(list(target_driver.keys()))
                    if is_un:
                        return _install_driver(retry + 1)  # 如果卸载成功, 则再次安装

                tmp_print('x 驱动重试失败, 不再重试, 请人工检查')
                return False
        else:
            tmp_print('√ 所需驱动全部已安装')
            return True
    except Exception as e:
        tmp_print(f'安装驱动失败, 发生错误: {e}')
        return False

def _add_sys_envs():
    """
    配置系统环境变量
    """
    # 先备份当前的系统环境变量
    is_backup_env = backup_envs()
    if not is_backup_env: return False
    # 配置系统环境变量
    is_add_env = add_need_envs()
    if not is_add_env: return False
    # 重启电脑
    if not test_mode:
        tmp_print('环境变量配置完毕, 5秒后重启电脑...(请勿操作)')
        time.sleep(3)
        os.system('shutdown -r -t 0')

""" ----------------------------------------------- 总流程 ----------------------------------------------- """

def install_envs():
    # 安装chrome
    if not _install_chrome(): return
    # 安装SDK/JDK/GRADLE
    if not _install_sdk_jdk_gradle(): return
    # 安装nodejs
    if not _install_nodejs(): return
    # 安装appium
    if not _install_appium(): return
    # 安装驱动
    if not _install_driver(): return
    # 配置系统环境变量
    if not _add_sys_envs(): return

def uninstall_envs():
    """
    注意: 以下步骤必须如下.
    """
    # 1. 把所有的所需软件(chrome, chromedriver)全部卸载
    if not _uninstall_chrome():
        tmp_print('x 卸载chrome失败, 进程停止')
        return
    # 2. 卸载appium
    if not _uninstall_appium():
        tmp_print('x 卸载appium失败, 进程停止')
        return
    # 3. 卸载nodejs
    if not _uninstall_nodejs():
        tmp_print('x 卸载nodejs失败, 进程停止')
        return
    # 4. 卸载驱动
    if not _uninstall_driver(list(target_driver.keys())):
        tmp_print('x 卸载驱动失败, 进程停止')
        return
    # 5. 环境变量全部还原为初始状态
    _restore_envs_result = _restore_sys_envs()
    # 6. (还原好系统环境前提下)把所有工程目录下的sdk, jdk , gradle 等目录全部删除
    if not _restore_envs_result:
        tmp_print('x 还原系统环境变量失败, 请手动检查')
    else:
        tmp_print('√ 还原系统环境变量完成')
    _uninst_sdk_jdk_gradle_result = _uninstall_sdk_jdk_gradle()

    tmp_print('=' * 30, '>>> 卸载操作结束', '=' * 30)

# install_envs()
# uninstall_envs()
pass
