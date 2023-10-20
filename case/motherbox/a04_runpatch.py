import os

from b00_checknet import *
from b01_checkenvs import *

def do_exe(pathc_dir):
    """
    执行脚本
    :param pathc_dir: 如 D:\autocase\patch\p_ap_match
    """
    try:
        # 查看指定目录下是否有apk文件 且 只有一个apk文件 且 apk文件名是ecoflow_oversea.apk
        files = os.listdir(pathc_dir)  # 获取指定目录下的所有文件
        apk_files = [f for f in files if f.endswith(".apk")]  # 使用列表解析找出所有以".apk"结尾的文件
        if len(apk_files) != 1:  # 检查是否只有一个APK文件且文件名为"ecoflow_oversea.apk"
            tmp_print('x apk文件检查不通过, 请检查脚本目录下是否有且只有一个apk文件')
            return False

        # 进入build/exe.win-amd64-3.11目录
        exe_build = os.path.join(pathc_dir, 'build', get_pack_dirname())
        e_files = os.listdir(str(exe_build))  # 获取指定目录下的所有文件
        # 查看是否有exe文件 且 只有一个exe文件
        exe_files = [f for f in e_files if f.endswith(".exe")]  # 使用列表解析找出所有以".exe"结尾的文件
        if len(exe_files) != 1:  # 检查是否只有一个APK文件且文件名为"ecoflow_oversea.apk"
            tmp_print('x exe文件检查不通过, 请检查脚本目录下是否有且只有一个exe文件')
            return False

        # 安装apk文件
        tmp_print('开始安装apk文件...')
        is_exist, info = where_cmd('adb')  # 查找adb的路径(is_exist为True, info为路径(注意是exe路径, 如果需要去掉exe, 可以使用os.path.dirname(info)))
        if not is_exist:
            tmp_print('x 未找到adb命令, 请检查环境变量是否已经安装adb')
            return False
        adb_command = f"adb install -r -t {pathc_dir}\\{apk_files[0]}"
        tmp_print(f'安装apk文件: {adb_command}')
        adb_shell(adb_command, True, os.path.dirname(info))
        time.sleep(5)
        tmp_print('安装apk文件完成')

        input('请先打开app,注册账号并登录(无需添加设备),如已经注册并登录,请按任意键继续...')

        # 执行exe文件
        tmp_print('开始执行exe文件...')
        exe_command = f"{exe_build}\\{exe_files[0]}"
        tmp_print(f'执行exe文件: {exe_command}')
        patch_exe = subprocess.Popen([exe_command], creationflags=subprocess.CREATE_NEW_CONSOLE)
        tmp_print("当前脚本进程ID:", patch_exe.pid)
        sys.exit()  # 退出母盒, 目的是禁止压测人员重复调起脚本
    except Exception as e:
        tmp_print(f'x 脚本执行失败, {e}')
        # 检查adb是否安装
        is_adb_install = check_adb_install()
        # 如果adb安装了, 则重启adb
        if is_adb_install: restart_adb()
        return False

def run_patch(func_cancel):
    """
    运行脚本
    :param func_cancel:  当前面板下点击取消的回调函数
    """
    try:
        # 检查是否有脚本目录以及该目录下是否有脚本目录
        if not os.path.exists(patch_root):
            tmp_print('x 此前没有下载过任何, 请先回到菜单下载脚本')
            # 创建脚本目录(不提示,直接创建)
            os.makedirs(patch_root)
            return False

        # 检查脚本根目录下是否有脚本子目录 {'p_ble_conn_delta': 'D:\\autocase\\patch\\p_ble_conn_delta',}
        patch_cdirs_dict = find_cdirs_prefix(patch_root, patch_cdir_prefix)
        if patch_cdirs_dict is None:
            tmp_print('x 脚本包没有可执行脚本, 请先回到菜单下载脚本')
            return False

        # 取出所有key, 每个key组成一个元祖 [(0, 'p_bleverify'),(1,'p_ota')] 并把元祖存放到一个列表中
        patch_cdirs_list = [(str(index), cdirname) for index, cdirname in enumerate(list(patch_cdirs_dict.keys()))]
        # 进入面板选择 '0'
        choice_patch = ['选择要执行的脚本', '请选择:', patch_cdirs_list]
        patch_seleted = choice_pancel(choice_patch[0], choice_patch[1], choice_patch[2], fun_cancel=func_cancel)
        tmp_print(f'当前选中: {str(patch_seleted)} -> {patch_cdirs_list[int(patch_seleted)]}')
        # 得到绝对路径 'D:\\autocase\\patch\\p_ble_conn_delta'
        local_path = "None"
        for tunple in patch_cdirs_list:
            if str(patch_seleted) in tunple[0]:
                local_path = patch_cdirs_dict[tunple[1]]
                break
        tmp_print(f'脚本地址: {local_path}')
        # 地址存在, 则执行脚本
        if os.path.exists(local_path):

            # 检查网络
            is_network_pass = check_all_nets()
            # 检查环境
            is_sys_pass = check_all_sys()
            # 如果网络或者环境变量不通过, 则不执行
            if not is_network_pass:
                tmp_print('x 网络检查不通过, 请检查网络')
                return False
            if not is_sys_pass:
                tmp_print('x 环境检查不通过, 请检查环境')
                return False

            # 正式调起脚本
            return do_exe(local_path)
        else:
            tmp_print(f'x 脚本目录不存在: {local_path}')
            # 创建脚本目录(不提示,直接创建)
            os.makedirs(local_path)
            return False
    except Exception as e:
        tmp_print(f'x 脚本执行失败, {e}')
        return False
