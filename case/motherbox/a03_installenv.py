import shutil

from b00_checknet import *
from b01_checkenvs import *

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
        if not is_network: return
        # 先清空并删除ChromeSetup目录
        if os.path.exists(str(chromesetup_dir)): shutil.rmtree(chromesetup_dir, onerror=del_rw)
        # 再重新创建ChromeSetup目录
        os.makedirs(chromesetup_dir)
        # 如果传入了chrome_infos(说明原先已安装), 则先卸载
        if chrome_infos is not None:
            tmp_print('正在卸载chrome...')
            # 在chrome_infos中查找卸载命令
            uninstall_cmd = next((str(item) for item in chrome_infos if '--uninstall' in str(item)), None)
            # 拼接强制卸载参数
            uninstall_cmd = uninstall_cmd + ' --force-uninstall'
            tmp_print(uninstall_cmd)
            # 执行卸载命令, 先卸载
            subprocess.run(uninstall_cmd, shell=True)
            time.sleep(5)
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
        return

    node_infos = check_exe('Node.js')
    # 先卸载 (如果不是直接安裝)
    if not direct_install:
        # 也要先判断下是否需要卸载
        if len(node_infos) > 0:
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
        new_node_v = check_exe('Node.js')[2]
        tmp_print(f'成功安装 Node.js({new_node_v})')
    except Exception as e:
        tmp_print(f'安装Node.js失败: {e}')

def _install_chrome():
    """
    安装chrome
    :return:  True 安装成功, False 安装失败
    """
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
    node_state, node_tip, node_type = check_nodejs()
    if not node_state:  # 不符合要求
        # 判断类型
        if node_type == NODE_NOT_INSTALL:
            tmp_print('未安装nodejs, 准备开始安装...')
            __reinstall_node(True)  # 直接安裝
        elif node_type == NODE_NOT_TARGET_VERSION:
            tmp_print('nodejs版本不匹配, 准备开始重新安装...')
            __reinstall_node()  # 先卸载再安装
        elif node_type == NPM_NOT_INSTALL:
            tmp_print('npm未安装, 准备开始重新安装...')
            __reinstall_node()  # 先卸载再安装
        elif node_type == NODE_NPM_ERROR:
            tmp_print('nodejs和npm获取信息异常, 准备开始重新安装...')
            __reinstall_node()  # 先卸载再安装
        else:
            tmp_print('nodejs已安装, 无需重装')
            return True
    else:
        tmp_print('nodejs已安装且符合要求, 无需重装')
        return True

_install_nodejs()

def install_envs():
    # 安装chrome
    if not _install_chrome(): return
    # 安装SDK/JDK/GRADLE
    if not _install_sdk_jdk_gradle(): return

if __name__ == '__main__':
    # check_nodejs()
    pass
